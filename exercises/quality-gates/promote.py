"""Promote f1-points-finish@candidate to @champion, but only if the gate report says it passed.

Step 4 of the release pipeline. It moves the alias @champion to the candidate version and
tags that version with who approved it, when, the gate results and the previous champion.
--rollback moves @champion back to the previous champion.

Usage:
    python exercises/quality-gates/promote.py --approver "Your Name"
    python exercises/quality-gates/promote.py --rollback --approver "Your Name"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import mlflow
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException

MODEL_NAME = "f1-points-finish"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def alias_version(client: MlflowClient, alias: str):
    """Return the model version behind the alias, or None if the alias is not set."""
    try:
        return client.get_model_version_by_alias(MODEL_NAME, alias)
    except MlflowException:
        return None


def write_summary(message: str):
    """In GitHub Actions, show the result on the run page too."""
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(f"### Promotion\n\n{message}\n")


def refuse(reason: str):
    message = f"REFUSED: {reason}"
    print(message)
    write_summary(message)
    sys.exit(1)


def check_report(report: dict, candidate) -> list[str]:
    """Return the reasons to refuse the promotion (empty when it may go ahead)."""
    if candidate is None:
        return [f"{MODEL_NAME} has no @candidate. Run train_candidate.py first."]
    if str(report.get("version")) != str(candidate.version):
        return [
            f"the gate report is for version {report.get('version')}, but @candidate is version "
            f"{candidate.version}. Run the gates again."
        ]
    reasons = [f"gate {g['gate']} {g['outcome']}: {g['detail']}" for g in report["gates"]
               if g["outcome"] in ("failed", "error")]
    if not reasons and not report["all_passed"]:
        reasons.append("no gate passed")
    return reasons


def print_gates(report: dict):
    for g in report["gates"]:
        label = "NOT CHECKED" if g["outcome"] == "skipped" else g["outcome"].upper()
        measured = ", ".join(f"{k} {v}" for k, v in g["measured"].items())
        print(f"  {label:<12} {g['gate']:<28} {measured}")


def promote(client: MlflowClient, report: dict, approver: str) -> str:
    candidate = alias_version(client, "candidate")
    print(f"Gate report for {MODEL_NAME} version {report.get('version')}:")
    print_gates(report)

    reasons = check_report(report, candidate)
    if reasons:
        refuse("the candidate cannot be promoted.\n" + "\n".join(f"- {r}" for r in reasons))

    skipped = [g["gate"] for g in report["gates"] if g["outcome"] == "skipped"]
    if skipped:
        print(f"WARNING: {len(skipped)} gates were not checked: {', '.join(skipped)}")

    champion = alias_version(client, "champion")
    previous = champion.version if champion else "none"
    if previous == candidate.version:
        return f"{MODEL_NAME} version {previous} is already @champion. Nothing to do."

    client.set_registered_model_alias(MODEL_NAME, "champion", candidate.version)
    tags = {
        "promoted_by": approver,
        "promoted_at": now(),
        "previous_champion": previous,
        "gates": ", ".join(f"{n} {o}" for o, n in report["counts"].items() if n),
        **{f"gate.{g['gate']}": g["outcome"] for g in report["gates"]},
    }
    for key, value in tags.items():
        client.set_model_version_tag(MODEL_NAME, candidate.version, key, str(value))
    return (
        f"PROMOTED: {MODEL_NAME} version {candidate.version} is now @champion "
        f"(previous champion: {previous}). Approved by {approver}."
    )


def rollback(client: MlflowClient, approver: str) -> str:
    champion = alias_version(client, "champion")
    if champion is None:
        refuse(f"{MODEL_NAME} has no @champion to roll back.")
    previous = champion.tags.get("previous_champion", "none")
    if previous == "none":
        refuse(f"version {champion.version} has no previous champion to go back to.")

    client.set_registered_model_alias(MODEL_NAME, "champion", previous)
    client.set_model_version_tag(MODEL_NAME, champion.version, "rolled_back_by", approver)
    client.set_model_version_tag(MODEL_NAME, champion.version, "rolled_back_at", now())
    return (
        f"ROLLED BACK: {MODEL_NAME} version {previous} is @champion again "
        f"(version {champion.version} removed by {approver})."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--approver", required=True, help="who approved this promotion")
    parser.add_argument("--report", type=Path, default=Path("gate_report.json"))
    parser.add_argument("--rollback", action="store_true", help="move @champion back to the previous champion")
    parser.add_argument("--tracking-uri", default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    args = parser.parse_args()
    mlflow.set_tracking_uri(args.tracking_uri)
    client = MlflowClient()

    if args.rollback:
        message = rollback(client, args.approver)
    else:
        if not args.report.exists():
            refuse(f"{args.report} not found. Run the quality gates first.")
        message = promote(client, json.loads(args.report.read_text()), args.approver)
    print(message)
    write_summary(message)


if __name__ == "__main__":
    main()
