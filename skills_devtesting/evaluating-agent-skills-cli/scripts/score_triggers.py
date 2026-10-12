#!/usr/bin/env python3
"""Score skill-selection results against labelled cases.

cases.json:   [{"id": "...", "prompt": "...", "expected": "skill-name" or null}, ...]
results.json: [{"id": "...", "selected": "skill-name" or null}, ...]

A null expected value means no skill should be selected for that prompt.
Every case id needs a result; missing ids are reported and not scored.
Standard library only.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_list(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON list")
    return data


def score(cases, results):
    selected_by_id = {}
    for row in results:
        if "id" not in row or "selected" not in row:
            raise ValueError("each result needs 'id' and 'selected'")
        selected_by_id[row["id"]] = row["selected"]

    tp, fp, fn = defaultdict(int), defaultdict(int), defaultdict(int)
    correct, scored, missing = 0, 0, []
    misses, false_positives = [], []

    for case in cases:
        if "id" not in case or "expected" not in case:
            raise ValueError("each case needs 'id' and 'expected'")
        cid, expected = case["id"], case["expected"]
        if cid not in selected_by_id:
            missing.append(cid)
            continue
        scored += 1
        selected = selected_by_id[cid]
        if selected == expected:
            correct += 1
            if expected:
                tp[expected] += 1
            continue
        if selected:
            fp[selected] += 1
            false_positives.append({"id": cid, "selected": selected, "expected": expected})
        if expected:
            fn[expected] += 1
            misses.append({"id": cid, "expected": expected, "selected": selected})

    skills = sorted(set(tp) | set(fp) | set(fn))
    per_skill = {}
    for skill in skills:
        predicted = tp[skill] + fp[skill]
        actual = tp[skill] + fn[skill]
        per_skill[skill] = {
            "precision": round(tp[skill] / predicted, 4) if predicted else None,
            "recall": round(tp[skill] / actual, 4) if actual else None,
            "true_positive": tp[skill],
            "false_positive": fp[skill],
            "false_negative": fn[skill],
        }

    return {
        "cases": len(cases),
        "scored": scored,
        "missing_results": missing,
        "accuracy": round(correct / scored, 4) if scored else None,
        "per_skill": per_skill,
        "misses": misses,
        "false_positives": false_positives,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cases", required=True, help="path to labelled cases JSON")
    parser.add_argument("--results", required=True, help="path to recorded selections JSON")
    args = parser.parse_args(argv)
    try:
        report = score(load_list(args.cases), load_list(args.results))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    json.dump(report, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
