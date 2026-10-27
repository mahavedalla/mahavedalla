
#!/usr/bin/env python3
"""
Find Markdown question files that have YAML front matter but no body.

A file is reported when:
- It begins with a YAML front-matter delimiter (---) on the first line.
- A closing delimiter (---) is found on a line by itself.
- Everything after that closing delimiter is whitespace.

This script is read-only: it does not modify question files.

Run from the repository root:
    python scripts/pyscripts/find_questions_without_body.py

Optional arguments:
    --questions-dir PATH   Directory to scan (default: questions)
    --output PATH          CSV report path
                           (default: scripts/md/questions_without_body.csv)
"""

import argparse
import csv
import sys
from pathlib import Path


def has_front_matter_but_no_body(text: str) -> tuple[bool, str]:
    """Return (matches, reason) for a Markdown document."""
    # Handle UTF-8 BOM and normalize line endings for inspection.
    normalized = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.splitlines()

    if not lines or lines[0].strip() != "---":
        return False, "No opening YAML delimiter on first line"

    # Front matter closes at the first subsequent delimiter line.
    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        return False, "No closing YAML delimiter found"

    body = "\n".join(lines[closing_index + 1 :])

    if not body.strip():
        return True, "No content after closing front matter"

    return False, "Body content exists"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find Markdown question files with front matter but no body."
    )
    parser.add_argument(
        "--questions-dir",
        type=Path,
        default=Path("questions"),
        help="Directory to scan (default: questions)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("scripts/md/questions_without_body.csv"),
        help="CSV report path "
             "(default: scripts/md/questions_without_body.csv)",
    )
    args = parser.parse_args()

    questions_dir = args.questions_dir

    if not questions_dir.is_dir():
        print(
            f"Error: questions directory not found: {questions_dir}",
            file=sys.stderr,
        )
        return 2

    matches = []
    scanned = 0

    markdown_files = sorted(
        path
        for path in questions_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".md"
    )

    for path in markdown_files:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            matches.append({
                "relative_path": path.as_posix(),
                "filename": path.name,
                "status": "REVIEW",
                "reason": "Could not decode as UTF-8",
            })
            continue
        except OSError as exc:
            matches.append({
                "relative_path": path.as_posix(),
                "filename": path.name,
                "status": "ERROR",
                "reason": str(exc),
            })
            continue

        scanned += 1
        is_match, reason = has_front_matter_but_no_body(text)

        if is_match:
            matches.append({
                "relative_path": path.as_posix(),
                "filename": path.name,
                "status": "MATCH",
                "reason": reason,
            })

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)

        with args.output.open(
            "w", newline="", encoding="utf-8-sig"
        ) as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=[
                    "relative_path",
                    "filename",
                    "status",
                    "reason",
                ],
            )
            writer.writeheader()
            writer.writerows(matches)

    except OSError as exc:
        print(f"Error writing CSV report: {exc}", file=sys.stderr)
        return 2

    match_count = sum(
        row["status"] == "MATCH" for row in matches
    )
    review_count = sum(
        row["status"] in {"REVIEW", "ERROR"} for row in matches
    )

    print(f"Markdown files scanned: {scanned}")
    print(f"Files with no body:      {match_count}")
    print(f"Files needing review:    {review_count}")
    print(f"CSV report written to:   {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
