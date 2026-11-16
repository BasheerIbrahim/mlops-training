"""Check a Locust run against the service-level objective in slo.yaml. Exit 1 if the run breaks it.

Locust writes <prefix>_stats.csv when you run it with --csv <prefix>. This script reads the
row for the endpoint in slo.yaml and compares the 95th percentile latency, the failure rate
and the number of requests with the objectives.

Usage:
    python exercises/serve-model/check_slo.py results/locust_stats.csv
    python exercises/serve-model/check_slo.py results/locust_stats.csv --slo exercises/serve-model/slo.yaml
"""

import argparse
import csv
import os
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent


def find_row(stats_csv: Path, endpoint: str) -> dict:
    """Return the row of the stats file for an endpoint such as 'POST /v1/predict'."""
    method, name = endpoint.split(" ", 1)
    with stats_csv.open() as f:
        for row in csv.DictReader(f):
            if row["Type"] == method and row["Name"] == name:
                return row
    sys.exit(f"ERROR: {stats_csv} has no row for {endpoint}. Did the load test send any request?")


def check(row: dict, objectives: dict) -> list[tuple]:
    """Return one (name, measured, limit, passed) per objective."""
    requests = int(row["Request Count"])
    failures = int(row["Failure Count"])
    rate = failures / requests if requests else 1.0
    p95 = float(row["95%"]) if requests else float("inf")
    return [
        ("requests", f"{requests}", f"at least {objectives['min_requests']}", requests >= objectives["min_requests"]),
        ("p95 latency", f"{p95:.0f} ms", f"at most {objectives['max_p95_ms']} ms", p95 <= objectives["max_p95_ms"]),
        ("failure rate", f"{rate:.2%}", f"at most {objectives['max_failure_rate']:.2%}",
         rate <= objectives["max_failure_rate"]),
    ]


def write_summary(title: str, results: list[tuple]):
    """In GitHub Actions, show the result on the run page too."""
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary:
        return
    lines = [f"### {title}", "", "| Objective | Measured | Limit | Result |", "|---|---|---|---|"]
    lines += [f"| {n} | {m} | {lim} | {'PASS' if ok else 'FAIL'} |" for n, m, lim, ok in results]
    with open(summary, "a") as f:
        f.write("\n".join(lines) + "\n\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stats_csv", type=Path, help="the <prefix>_stats.csv file that Locust wrote")
    parser.add_argument("--slo", type=Path, default=HERE / "slo.yaml")
    args = parser.parse_args()

    slo = yaml.safe_load(args.slo.read_text())
    results = check(find_row(args.stats_csv, slo["endpoint"]), slo["objectives"])

    print(f"SLO check for {slo['endpoint']} ({args.stats_csv}):")
    for name, measured, limit, ok in results:
        print(f"  {'PASS' if ok else 'FAIL':<5} {name:<13} {measured:>9}   {limit}")
    broken = [name for name, _, _, ok in results if not ok]
    verdict = f"SLO BROKEN: {', '.join(broken)}" if broken else "SLO MET"
    print(verdict)
    write_summary(f"Service-level objective: {verdict}", results)
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
