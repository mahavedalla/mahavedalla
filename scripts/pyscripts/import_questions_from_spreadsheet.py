
import argparse
import csv
import json
import re
import unicodedata
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = (
    ROOT
    / "scripts"
    / "files"
    / "07-09-26_Mahavedalla Temporary.csv"
)

OUTPUT_DIR = ROOT / "staged_questions"
TODAY = date.today().strftime("%m-%d-%Y")

REQUIRED_COLUMNS = [
    "Date Entered",
    "Question",
    "Category",
    "Sutta References",
    "Tags",
    "Notes",
]


def clean_text(value):
    """Trim whitespace and remove asterisks from imported text."""
    return (value or "").strip().replace("*", "")


def yaml_value(value):
    """Return plain, unquoted YAML text."""
    return value


def make_slug(question):
    """Create a filesystem-safe filename from a question."""
    normalized = unicodedata.normalize("NFKD", question)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower())
    return slug.strip("-")[:90].strip("-") or "untitled-question"


def make_markdown(row):
    question = clean_text(row["Question"])

    fields = {
        "Question": question,
        "Category": clean_text(row["Category"]),
        "Tags": clean_text(row["Tags"]),
        "Sutta References": clean_text(row["Sutta References"]),
        "Date Entered": clean_text(row["Date Entered"]),
        "Last Revised": TODAY,
        "Review Status": "Not started",
        "Level": "",
        "Priority": "",
        "Number": "",
    }

    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {yaml_value(value)}")

    lines.extend([
        "Draft: true",
        "---",
        "",
        f"# {question}",
        "",
        "## Bibliography",
        "",
        "<!-- ",
        "",
        "Notes:",
        "",
        clean_text(row["Notes"]),
        "",
        "",
        "",
        "-->",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Import spreadsheet questions into staged Markdown files."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Import only the first N valid questions; for testing, use --limit 5.",
    )
    args = parser.parse_args()

    if not CSV_PATH.exists():
        raise SystemExit(f"CSV file not found: {CSV_PATH}")

    with CSV_PATH.open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            raise SystemExit("The CSV has no header row.")

        missing_columns = [
            name for name in REQUIRED_COLUMNS
            if name not in reader.fieldnames
        ]
        if missing_columns:
            raise SystemExit(
                "Missing required CSV columns: "
                + ", ".join(missing_columns)
            )

        rows = list(reader)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    seen_questions = set()
    created = 0
    skipped = 0
    issues = []

    for csv_row_number, row in enumerate(rows, start=2):
        question = clean_text(row.get("Question"))

        if not question:
            skipped += 1
            issues.append(
                f"CSV row {csv_row_number}: skipped; Question is blank."
            )
            continue

        normalized_question = question.casefold()

        if normalized_question in seen_questions:
            skipped += 1
            issues.append(
                f"CSV row {csv_row_number}: skipped duplicate question: "
                f"{question}"
            )
            continue

        seen_questions.add(normalized_question)

        if args.limit is not None and created >= args.limit:
            break

        filename = f"{make_slug(question)}.md"
        destination = OUTPUT_DIR / filename

        if destination.exists():
            skipped += 1
            issues.append(
                f"CSV row {csv_row_number}: skipped; file already exists: "
                f"{filename}"
            )
            continue

        markdown = make_markdown(row)

        # Safety check: generated files must contain no asterisks.
        if "*" in markdown:
            raise ValueError(
                f"Asterisk found in generated output for CSV row "
                f"{csv_row_number}."
            )

        destination.write_text(markdown, encoding="utf-8")
        created += 1
        print(f"Created: {destination.relative_to(ROOT)}")

    print()
    print(f"CSV rows read: {len(rows)}")
    print(f"Files created: {created}")
    print(f"Rows/files skipped: {skipped}")
    print(f"Last Revised date: {TODAY}")
    print(f"Output folder: {OUTPUT_DIR.relative_to(ROOT)}")

    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"- {issue}")


if __name__ == "__main__":
    main()
