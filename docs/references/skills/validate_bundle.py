#!/usr/bin/env python3
"""Validate a Majlis Academy Brain: OKF v0.2 conformance + the majlis-academy/1 profile.

usage:
  validate_bundle.py <brain-dir> [--package /packages/<id>] [--now YYYY-MM-DD] [--json]

Checks
  OKF §11   every non-reserved .md has parseable frontmatter with a non-empty `type`
  profile   required keys per type, enum values, ID references that resolve
  G1        (with --package) every Domain Concept the package reaches meets `min_trust`
  G5        (with --package) no reached concept is stale or deprecated
Exit code 1 when any error is found.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

RESERVED = {"index.md", "log.md"}
TIERS = ["unverified", "machine-confirmed", "human-reviewed"]
BLOOM = ["remember", "understand", "apply", "analyse", "evaluate", "create"]
AUDIENCE = {"executive", "practitioner", "engineer", "mixed"}
FORMATS = {"executive-briefing", "bootcamp", "lab", "capstone", "hackathon", "accelerator",
           "micro-learning", "classroom-workshop"}
KINDS = {"mcq", "short-answer", "task", "rubric-line", "lab-check"}
MODES = {"online", "classroom", "hybrid"}
CLASSES = {"public", "internal", "client-confidential"}
STATUS = {"draft", "stable", "deprecated"}

PROFILE = {
    "Domain Concept": {"req": ["title", "description", "generated", "sources", "classification",
                               "framework_refs", "stale_after"]},
    "Learning Objective": {"req": ["title", "description", "generated", "bloom_level", "audience",
                                   "derives_from"], "refs": {"derives_from": ["Domain Concept"]}},
    "Assessment Item": {"req": ["title", "generated", "objective", "bloom_level", "kind", "difficulty"],
                        "refs": {"objective": ["Learning Objective"]}},
    "Learning Activity": {"req": ["title", "generated", "objectives", "mode", "duration_min", "pattern"],
                          "refs": {"objectives": ["Learning Objective"]}},
    "Lab": {"req": ["title", "description", "generated", "objectives", "environment", "duration_min",
                    "grader", "data"],
            "refs": {"objectives": ["Learning Objective"], "environment": ["Lab Environment"],
                     "grader": ["Attested Computation"]}},
    "Lab Environment": {"req": ["title", "runtime", "resource"]},
    "Reference": {"req": ["title"]},
    "Attested Computation": {"req": ["title", "runtime", "executor", "attester"]},
    "Learning Package": {"req": ["title", "description", "generated", "format", "audience", "uses",
                                 "release", "min_trust"], "refs": {"uses": None}},
}
LINK_KEYS = ("derives_from", "objective", "objectives", "environment", "grader", "uses")


def parse_dt(v):
    if isinstance(v, dt.datetime):
        return v if v.tzinfo else v.replace(tzinfo=dt.timezone.utc)
    if isinstance(v, dt.date):
        return dt.datetime(v.year, v.month, v.day, tzinfo=dt.timezone.utc)
    if isinstance(v, str):
        s = v.strip().replace("Z", "+00:00")
        try:
            d = dt.datetime.fromisoformat(s)
            return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
        except ValueError:
            return None
    return None


def norm_id(v):
    v = str(v).strip()
    if not v.startswith("/"):
        v = "/" + v
    return v[:-3] if v.endswith(".md") else v


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def load(root):
    concepts, errors = {}, []
    for d, _, files in os.walk(root):
        if "/.git" in d:
            continue
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            path = os.path.join(d, f)
            rel = "/" + os.path.relpath(path, root).replace(os.sep, "/")
            text = open(path, encoding="utf-8").read()
            if f in RESERVED:
                continue
            m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
            if not m:
                errors.append((rel, "OKF §11: no YAML frontmatter"))
                continue
            try:
                fm = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError as e:
                errors.append((rel, f"OKF §11: frontmatter does not parse ({e.__class__.__name__})"))
                continue
            if not isinstance(fm, dict) or not str(fm.get("type", "")).strip():
                errors.append((rel, "OKF §11: missing or empty `type`"))
                continue
            concepts[rel[:-3]] = {"fm": fm, "body": m.group(2), "path": rel}
    return concepts, errors


def tier(fm):
    v = fm.get("verified")
    if not v:
        return "unverified"
    actors = [str(x.get("by", "")) for x in as_list(v) if isinstance(x, dict)]
    return "human-reviewed" if any(a.startswith("human:") for a in actors) else "machine-confirmed"


def check_profile(concepts):
    errors, warnings = [], []
    for cid, c in concepts.items():
        fm, t = c["fm"], c["fm"]["type"]
        rule = PROFILE.get(t)
        if rule is None:
            warnings.append((cid, f"type `{t}` is not in the majlis-academy/1 profile"))
            continue
        for k in rule["req"]:
            if fm.get(k) in (None, "", []):
                errors.append((cid, f"{t}: missing `{k}`"))
        if fm.get("status", "stable") not in STATUS:
            errors.append((cid, f"`status` must be one of {sorted(STATUS)}"))
        g = fm.get("generated")
        if isinstance(g, dict) and not str(g.get("by", "")).strip():
            errors.append((cid, "`generated.by` is required"))
        for v in as_list(fm.get("verified")):
            if not isinstance(v, dict) or not v.get("by") or parse_dt(v.get("at")) is None:
                errors.append((cid, "`verified` entries need `by` and an ISO `at`"))
        if "stale_after" in fm and parse_dt(fm["stale_after"]) is None:
            errors.append((cid, "`stale_after` is not an ISO datetime"))
        if t == "Domain Concept":
            if fm.get("classification") not in CLASSES:
                errors.append((cid, f"`classification` must be one of {sorted(CLASSES)}"))
            ids = [s.get("id") for s in as_list(fm.get("sources")) if isinstance(s, dict)]
            if any(not isinstance(s, dict) or not s.get("resource") for s in as_list(fm.get("sources"))):
                errors.append((cid, "each `sources` entry needs `resource`"))
            for label in re.findall(r"\[\^([^\]]+)\]", c["body"]):
                if label not in ids:
                    errors.append((cid, f"footnote [^{label}] has no matching `sources[].id`"))
        if t in ("Learning Objective", "Assessment Item") and fm.get("bloom_level") not in BLOOM:
            errors.append((cid, f"`bloom_level` must be one of {BLOOM}"))
        if t in ("Learning Objective", "Learning Package") and fm.get("audience") not in AUDIENCE:
            errors.append((cid, f"`audience` must be one of {sorted(AUDIENCE)}"))
        if t == "Learning Objective" and "# Statement" not in c["body"]:
            errors.append((cid, "Learning Objective needs a `# Statement` section"))
        if t == "Assessment Item":
            if fm.get("kind") not in KINDS:
                errors.append((cid, f"`kind` must be one of {sorted(KINDS)}"))
            if fm.get("difficulty") not in (1, 2, 3):
                errors.append((cid, "`difficulty` must be 1, 2 or 3"))
        if t == "Learning Activity" and fm.get("mode") not in MODES:
            errors.append((cid, f"`mode` must be one of {sorted(MODES)}"))
        if t == "Lab" and fm.get("data") not in ("synthetic", "client-approved"):
            errors.append((cid, "`data` must be `synthetic` or `client-approved`"))
        if t == "Lab" and fm.get("data") == "client-approved":
            warnings.append((cid, "lab uses client-approved data: record decision D4"))
        if t == "Learning Package":
            if fm.get("format") not in FORMATS:
                errors.append((cid, f"`format` must be one of {sorted(FORMATS)}"))
            if fm.get("min_trust") not in TIERS:
                errors.append((cid, f"`min_trust` must be one of {TIERS}"))
            if fm.get("format") == "executive-briefing" and fm.get("min_trust") != "human-reviewed":
                errors.append((cid, "executive briefings need `min_trust: human-reviewed`"))
        for key, allowed in (rule.get("refs") or {}).items():
            for ref in as_list(fm.get(key)):
                rid = norm_id(ref)
                if rid not in concepts:
                    errors.append((cid, f"`{key}` points to {rid}, which does not exist"))
                elif allowed and concepts[rid]["fm"]["type"] not in allowed:
                    errors.append((cid, f"`{key}` must point to {allowed}, not {concepts[rid]['fm']['type']}"))
        if t == "Assessment Item":
            oid = norm_id(fm.get("objective", ""))
            if oid in concepts and concepts[oid]["fm"].get("bloom_level") != fm.get("bloom_level"):
                warnings.append((cid, "bloom_level differs from its objective (gate G2)"))
        if fm.get("classification") == "client-confidential":
            warnings.append((cid, "client-confidential: keep this concept out of shared bundles"))
    return errors, warnings


def reach(concepts, start):
    """Every concept reachable from `start` through the profile's ID keys."""
    seen, stack = set(), [start]
    while stack:
        cid = stack.pop()
        if cid in seen or cid not in concepts:
            continue
        seen.add(cid)
        fm = concepts[cid]["fm"]
        for k in LINK_KEYS:
            stack.extend(norm_id(r) for r in as_list(fm.get(k)))
    # assessment items that check a reached objective belong to the package too
    for cid, c in concepts.items():
        if c["fm"]["type"] == "Assessment Item" and norm_id(c["fm"].get("objective", "")) in seen:
            seen.add(cid)
    return seen


def check_gates(concepts, pkg, now):
    errors, warnings = [], []
    if pkg not in concepts or concepts[pkg]["fm"]["type"] != "Learning Package":
        return [(pkg, "not a Learning Package in this bundle")], []
    need = TIERS.index(concepts[pkg]["fm"].get("min_trust", "unverified"))
    for cid in sorted(reach(concepts, pkg)):
        fm = concepts[cid]["fm"]
        if fm["type"] == "Domain Concept" and TIERS.index(tier(fm)) < need:
            errors.append((cid, f"G1: tier {tier(fm)} is below min_trust {TIERS[need]}"))
        sa = parse_dt(fm.get("stale_after")) if fm.get("stale_after") else None
        if sa and now >= sa:
            errors.append((cid, f"G5: stale since {sa.date().isoformat()}"))
        if fm.get("status") == "deprecated":
            errors.append((cid, "G5: deprecated"))
        if fm.get("status") == "draft" and fm["type"] == "Domain Concept":
            errors.append((cid, "G1: Domain Concept is still `draft`"))
    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brain")
    ap.add_argument("--package")
    ap.add_argument("--now")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    now = parse_dt(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    concepts, errors = load(a.brain)
    e2, warnings = check_profile(concepts)
    errors += e2
    if a.package:
        e3, w3 = check_gates(concepts, norm_id(a.package), now)
        errors += e3
        warnings += w3
    tiers = {}
    for c in concepts.values():
        if c["fm"]["type"] == "Domain Concept":
            tiers[tier(c["fm"])] = tiers.get(tier(c["fm"]), 0) + 1
    if a.json:
        print(json.dumps({"concepts": len(concepts), "tiers": tiers,
                          "errors": [{"id": i, "msg": m} for i, m in errors],
                          "warnings": [{"id": i, "msg": m} for i, m in warnings]}, indent=2))
    else:
        print(f"Brain: {a.brain} · {len(concepts)} concepts · domain-concept tiers: {tiers or 'none'}")
        for label, items in (("ERROR", errors), ("WARN", warnings)):
            for i, m in items:
                print(f"{label:5} {i}: {m}")
        print("RESULT:", "FAIL" if errors else "PASS", f"({len(errors)} errors, {len(warnings)} warnings)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
