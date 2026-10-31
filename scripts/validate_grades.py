#!/usr/bin/env python3
"""Validate a Chaoxing grading manifest before scores are submitted."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
REQUIRED_EVIDENCE_FOR_100 = {
    "purpose",
    "process",
    "results",
    "analysis",
    "reflection",
    "originality",
    "formatting",
}
def load_manifest(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Manifest root must be an object.")
    return data
def validate(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    minimum = data.get("minimum_score", 0)
    grades = data.get("grades")
    if not isinstance(minimum, (int, float)):
        errors.append("minimum_score must be numeric.")
    if not isinstance(grades, list) or not grades:
        return errors + ["grades must be a non-empty array."], warnings
    seen_students: set[tuple[str, str]] = set()
    seen_attachments: dict[str, str] = {}
    for index, row in enumerate(grades, start=1):
        prefix = f"grades[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        name = str(row.get("name", "")).strip()
        student_id = str(row.get("student_id", "")).strip()
        score = row.get("score")
        attachment_id = str(row.get("attachment_id") or "").strip()
        if not name:
            errors.append(f"{prefix}.name is required.")
        if not student_id:
            errors.append(f"{prefix}.student_id is required.")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            errors.append(f"{prefix}.score must be numeric.")
            continue
        if score < minimum or score > 100:
            errors.append(
                f"{prefix}.score={score} is outside [{minimum}, 100]."
            )
        student_key = (name, student_id)
        if student_key in seen_students:
            errors.append(f"Duplicate student: {name} ({student_id}).")
        seen_students.add(student_key)
        if score <= 70 and not str(row.get("comment", "")).strip():
            errors.append(f"{prefix} requires an issue-specific comment for score <= 70.")
        if attachment_id:
            prior = seen_attachments.get(attachment_id)
            if prior:
                warnings.append(
                    f"Attachment reused by {prior} and {name} ({student_id}); verify independently."
                )
            seen_attachments[attachment_id] = name
        if score == 100:
            evidence = row.get("evidence", {})
            if not isinstance(evidence, dict):
                errors.append(f"{prefix}.evidence must be an object for a 100 score.")
            else:
                missing = sorted(
                    key
                    for key in REQUIRED_EVIDENCE_FOR_100
                    if evidence.get(key) is not True
                )
                if missing:
                    errors.append(
                        f"{prefix} cannot be 100; missing evidence: {', '.join(missing)}."
                    )
        if score >= 80 and row.get("topic_mismatch") is True:
            errors.append(f"{prefix} has a topic mismatch but is scored 80 or above.")
    return errors, warnings
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = load_manifest(args.manifest)
        errors, warnings = validate(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK: {len(data['grades'])} grades validated.")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
