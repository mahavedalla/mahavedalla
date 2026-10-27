
#!/usr/bin/env python3
"""
Export front matter from every Markdown question into a CSV.

Input:
    questions/**/*.md

Output:
    question_front_matter_export.csv (repository root)

Original Markdown files are read-only and are never modified.
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(
        "Missing dependency: PyYAML\n"
        "Install it with: python3 -m pip install PyYAML"
    )


# Fields from the standard Mahavedalla question template.
# These columns will appear first, in this order.
STANDARD_FIELDS = [
    "Question",
    "Category",
    "Tags",
    "Sutta References",
    "Date Entered",
    "Last Revised",
    "Review Status",
    "Level",
    "Priority",
    "Number",
    "Draft",
]


def read_front_matter(path):
    """Return (metadata, status) for one Markdown file."""

    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return {}, f"Read error: {exc}"

    lines = text.splitlines()

    # YAML front matter must begin at the start of the file.
    if not lines or lines[0].strip() != "---":
        return {}, "Missing opening delimiter"

    # Find the closing front-matter delimiter.
    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        ),
        None,
    )

    if closing_index is None:
        return {}, "Missing closing delimiter"

    raw_front_matter = "\n".join(lines[1:closing_index])

    try:
        metadata = yaml.safe_load(raw_front_matter)
    except yaml.YAMLError as exc:
        message = str(exc).splitlines()[0]
        return {}, f"Invalid YAML: {message}"

    if metadata is None:
        return {}, "Empty front matter"

    if not isinstance(metadata, dict):
        return {}, "Front matter is not a key-value mapping"

    # CSV headers must be strings.
    metadata = {
        str(key): value
        for key, value in metadata.items()
    }

    return metadata, "OK"


def csv_value(value):
    """Convert YAML values into readable, unambiguous CSV cell values."""

    if value is None:
        return ""

    if isinstance(value, bool):
        return str(value).lower()

    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
            sort_keys=True,
        )

    return str(value)


def main():
    # Expected location:
    # repository/scripts/pyscripts/export_question_frontmatter.py
    root = Path(__file__).resolve().parents[2]
    questions_dir = root / "questions"
    output_path = root / "scripts"/ "md" / "question_front_matter_export.csv"

    if not questions_dir.is_dir():
        sys.exit(
            f"Error: questions directory not found: {questions_dir}"
        )

    # Find Markdown files recursively, including any uppercase .MD extensions.
    files = sorted(
        (
            path
            for path in questions_dir.rglob("*")
            if path.is_file() and path.suffix.lower() == ".md"
        ),
        key=lambda path: path.as_posix().casefold(),
    )

    records = []

    for path in files:
        metadata, status = read_front_matter(path)

        records.append({
            "File Path": path.relative_to(root).as_posix(),
            "Metadata": metadata,
            "Front Matter Status": status,
        })

    # Collect every front-matter field found in the repository.
    discovered_fields = {
        field
        for record in records
        for field in record["Metadata"]
    }

    # Keep standard fields first; append any additional fields alphabetically.
    extra_fields = sorted(
        discovered_fields.difference(STANDARD_FIELDS),
        key=str.casefold,
    )

    columns = [
        "File Path",
        *STANDARD_FIELDS,
        *extra_fields,
        "Front Matter Status",
    ]

    # Write one CSV row per Markdown file.
    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=columns,
            extrasaction="ignore",
        )
        writer.writeheader()

        for record in records:
            row = {
                field: csv_value(value)
                for field, value in record["Metadata"].items()
            }

            row["File Path"] = record["File Path"]
            row["Front Matter Status"] = record["Front Matter Status"]

            writer.writerow(row)

    # Summarize successful and unsuccessful parses.
    status_counts = Counter(
        record["Front Matter Status"]
        for record in records
    )

    print(f"Questions directory: {questions_dir}")
    print(f"Markdown files processed: {len(files)}")
    print(f"Front-matter fields exported: {len(discovered_fields)}")
    print(f"CSV columns: {len(columns)}")
    print(f"Files with front-matter issues: "
          f"{len(files) - status_counts.get('OK', 0)}")

    print("\nFront-matter status summary:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print(f"\nCSV export written to: {output_path}")


if __name__ == "__main__":
    main()
