
#!/usr/bin/env python3
"""
Append the standard body scaffold to question files that have YAML
front matter but no body.

Only files with a nonblank, recoverable Question field are eligible.
Existing front matter is preserved. Files are never deleted.

Run from the repository root:

    python scripts/pyscripts/repair_questions_without_body.py

Preview only (default):
    python scripts/pyscripts/repair_questions_without_body.py

Apply changes:
    python scripts/pyscripts/repair_questions_without_body.py --apply

Optional arguments:
    --questions-dir PATH
    --report PATH
"""

import argparse
import ast
import csv
import json
import re
import sys
from pathlib import Path


DEFAULT_REPORT = Path("scripts/md/question_body_repair_report.csv")


def find_front_matter(text):
    """Return (opening_end, closing_start, closing_end), or None."""
    # Allow a UTF-8 BOM without changing the original text.
    start = 1 if text.startswith("\ufeff") else 0

    opening = re.match(
        r"---[ \t]*(?:\r\n|\n|\r|$)",
        text[start:],
    )
    if not opening:
        return None

    opening_end = start + opening.end()

    closing = re.search(
        r"(?m)^---[ \t]*(?:\r\n|\n|\r|$)",
        text[opening_end:],
    )
    if not closing:
        return None

    closing_start = opening_end + closing.start()
    closing_end = opening_end + closing.end()

    return opening_end, closing_start, closing_end


def extract_question(front_matter):
    """
    Extract a simple, single-line YAML Question value.

    Blank values and complex YAML forms are skipped rather than guessed.
    """
    for line in front_matter.splitlines():
        match = re.match(r"^[ \t]*Question[ \t]*:[ \t]*(.*?)[ \t]*$", line)
        if not match:
            continue

        value = match.group(1).strip()

        if not value or value in {"|", ">", "|-", ">-", "|+", ">+"}:
            return None, "Question field is blank or multiline"

        # Decode simple quoted YAML strings conservatively.
        if value.startswith("'"):
            if len(value) < 2 or not value.endswith("'"):
                return None, "Question has ambiguous single-quoted value"
            question = value[1:-1].replace("''", "'")

        elif value.startswith('"'):
            try:
                question = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return None, "Question has an unsupported quoted value"

        else:
            # Do not interpret YAML comments or special syntax as question text.
            if re.search(r"[ \t]#", value) or value.startswith(
                ("[", "{", "&", "*", "!", "|", ">", ">", "%")
            ):
                return None, "Question has an ambiguous YAML value"
            question = value

        question = question.strip()

        if not question:
            return None, "Question field is blank"

        if "\n" in question or "\r" in question:
            return None, "Question is not a single-line value"

        return question, "Question recovered from front matter"

    return None, "Question field not found"


def make_scaffold(question, newline):
    """Build the standard body scaffold."""
    return newline.join([
        f"**# {question}**",
        "",
        "**## Bibliography**",
        "",
        "<!--&#x20;",
        "",
        "Notes:",
        "",
        "",
        "-->",
        "",
    ])


def main():
    parser = argparse.ArgumentParser(
        description="Append missing question-body scaffolds."
    )
    parser.add_argument(
        "--questions-dir",
        type=Path,
        default=Path("questions"),
        help="Directory to scan (default: questions)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"CSV report path (default: {DEFAULT_REPORT})",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually append scaffolds; otherwise preview only",
    )
    args = parser.parse_args()

    if not args.questions_dir.is_dir():
        print(
            f"Error: directory not found: {args.questions_dir}",
            file=sys.stderr,
        )
        return 2

    report_rows = []
    scanned = 0
    eligible = 0
    updated = 0
    skipped = 0

    files = sorted(
        p for p in args.questions_dir.rglob("*")
        if p.is_file() and p.suffix.lower() == ".md"
    )

    for path in files:
        try:
            original_bytes = path.read_bytes()
            text = original_bytes.decode("utf-8")
        except UnicodeDecodeError:
            report_rows.append({
                "path": path.as_posix(),
                "status": "SKIP",
                "reason": "File is not valid UTF-8",
            })
            skipped += 1
            continue
        except OSError as exc:
            report_rows.append({
                "path": path.as_posix(),
                "status": "ERROR",
                "reason": str(exc),
            })
            skipped += 1
            continue

        scanned += 1
        bounds = find_front_matter(text)

        if bounds is None:
            continue

        opening_end, closing_start, closing_end = bounds
        body = text[closing_end:]

        # Do not touch files that already contain body content.
        if body.strip():
            continue

        front_matter = text[opening_end:closing_start]
        question, reason = extract_question(front_matter)

        if question is None:
            report_rows.append({
                "path": path.as_posix(),
                "status": "SKIP",
                "reason": reason,
            })
            skipped += 1
            continue

        eligible += 1
        newline = "\r\n" if "\r\n" in text else "\n"
        scaffold = make_scaffold(question, newline)

        if not args.apply:
            report_rows.append({
                "path": path.as_posix(),
                "status": "PREVIEW",
                "reason": "Would append standard scaffold",
            })
            continue

        # Append only: preserve all existing bytes and add the scaffold.
        # Add a separator before the scaffold without altering existing text.
        if text.endswith(("\n", "\r")):
            prefix = newline
        else:
            prefix = newline + newline

        try:
            with path.open("ab") as file:
                file.write((prefix + scaffold).encode("utf-8"))

            updated += 1
            report_rows.append({
                "path": path.as_posix(),
                "status": "UPDATED",
                "reason": "Appended standard scaffold",
            })
        except OSError as exc:
            report_rows.append({
                "path": path.as_posix(),
                "status": "ERROR",
                "reason": str(exc),
            })
            skipped += 1

    try:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open(
            "w", newline="", encoding="utf-8-sig"
        ) as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=["path", "status", "reason"],
            )
            writer.writeheader()
            writer.writerows(report_rows)
    except OSError as exc:
        print(f"Error writing report: {exc}", file=sys.stderr)
        return 2

    print(f"Markdown files scanned: {scanned}")
    print(f"Eligible files:         {eligible}")

    if args.apply:
        print(f"Files updated:          {updated}")
    else:
        print(f"Would update:           {eligible}")
        print("Preview only; no question files were changed.")

    print(f"Files skipped:          {skipped}")
    print(f"Report:                 {args.report}")

    if not args.apply:
        print("\nTo apply the changes, rerun with --apply.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
