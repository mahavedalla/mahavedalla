
from pathlib import Path
import re
from collections import Counter


ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_DIR = ROOT / "questions"
REPORT_PATH = (
    ROOT / "scripts" / "md" / "metadata_trailing_whitespace_report.md"
)

EXCLUDED_FIELDS = {
    "Question",
    "Date Entered",
    "Last Revised",
    "Review Status",
    "Draft",
}

FIELD_PATTERN = re.compile(r"^([A-Za-z][A-Za-z0-9 _-]*):")
TRAILING_PATTERN = re.compile(r"[ \t]+$")


def inspect_file(path):
    findings = []
    front_matter_seen = False
    inside_front_matter = False

    with path.open(
        "r", encoding="utf-8", errors="replace", newline=""
    ) as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\r\n")

            if line_number == 1 and line.strip() == "---":
                inside_front_matter = True
                front_matter_seen = True
                continue

            if not inside_front_matter:
                continue

            if line.strip() == "---":
                inside_front_matter = False
                break

            field_match = FIELD_PATTERN.match(line)
            if not field_match:
                continue

            field_name = field_match.group(1).strip()

            if field_name in EXCLUDED_FIELDS:
                continue

            whitespace_match = TRAILING_PATTERN.search(line)
            if not whitespace_match:
                continue

            trailing = whitespace_match.group()

            findings.append({
                "line": line_number,
                "field": field_name,
                "spaces": trailing.count(" "),
                "tabs": trailing.count("\t"),
            })

    return findings, front_matter_seen


def find_notes_comment_openers(path):
    """Find exact '<!-- ' openers without changing the file."""
    findings = []

    with path.open(
        "r", encoding="utf-8", errors="replace", newline=""
    ) as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\r\n")

            if "<!-- " in line:
                findings.append({
                    "line": line_number,
                    "text": line.strip(),
                })

    return findings


def main():
    if not QUESTIONS_DIR.is_dir():
        raise SystemExit(
            f"Questions directory not found: {QUESTIONS_DIR}"
        )

    files = sorted(QUESTIONS_DIR.rglob("*.md"))
    all_findings = []
    files_without_front_matter = []
    field_counts = Counter()
    comment_openers = []

    # First loop: audit front-matter metadata.
    for path in files:
        findings, has_front_matter = inspect_file(path)

        if not has_front_matter:
            files_without_front_matter.append(path)

        if findings:
            all_findings.append((path, findings))
            for finding in findings:
                field_counts[finding["field"]] += 1

    # Second loop: find HTML comment openers across Markdown files.
    for path in files:
        for finding in find_notes_comment_openers(path):
            comment_openers.append((
                path.relative_to(ROOT).as_posix(),
                finding["line"],
                finding["text"],
            ))

    # Build the report.
    report = [
        "# Metadata Trailing Whitespace Audit",
        "",
        "Read-only audit. No question files were modified.",
        "",
        f"- Markdown files scanned: {len(files)}",
        f"- Files with metadata findings: {len(all_findings)}",
        f"- Metadata lines with trailing whitespace: "
        f"{sum(field_counts.values())}",
        f"- Files without front matter: {len(files_without_front_matter)}",
        "",
        "## Excluded fields",
        "",
    ]

    report.extend(f"- `{field}`" for field in sorted(EXCLUDED_FIELDS))
    report.extend(["", "## Counts by metadata field", ""])

    if field_counts:
        report.extend([
            "| Field | Matching lines |",
            "|---|---:|",
        ])
        for field, count in sorted(field_counts.items()):
            report.append(f"| `{field}` | {count} |")
    else:
        report.append("No matching metadata whitespace found.")

    report.extend(["", "## Metadata findings", ""])

    if not all_findings:
        report.append("No findings.")
    else:
        for path, findings in all_findings:
            relative_path = path.relative_to(ROOT).as_posix()
            report.extend([
                f"### `{relative_path}`",
                "",
                "| Line | Field | Trailing spaces | Trailing tabs |",
                "|---:|---|---:|---:|",
            ])

            for finding in findings:
                report.append(
                    f"| {finding['line']} | `{finding['field']}` "
                    f"| {finding['spaces']} | {finding['tabs']} |"
                )

            report.append("")

    # Separate section for the exact HTML comment opener.
    report.extend([
        "",
        "## HTML comment openers (`<!-- `)",
        "",
        f"Occurrences found: {len(comment_openers)}",
        "",
    ])

    if comment_openers:
        report.extend([
            "| File | Line | Matching line |",
            "|---|---:|---|",
        ])

        for file_path, line_number, text in comment_openers:
            safe_text = text.replace("|", "\\|")
            report.append(
                f"| `{file_path}` | {line_number} | `{safe_text}` |"
            )
    else:
        report.append("No exact '<!-- ' openers found.")

    if files_without_front_matter:
        report.extend(["", "## Files without front matter", ""])
        report.extend(
            f"- `{path.relative_to(ROOT).as_posix()}`"
            for path in files_without_front_matter
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(report).rstrip() + "\n",
        encoding="utf-8",
    )

    print("Audit complete. No question files were modified.")
    print(f"Markdown files scanned: {len(files)}")
    print(f"Files with metadata findings: {len(all_findings)}")
    print(f"Metadata lines with trailing whitespace: "
          f"{sum(field_counts.values())}")
    print(f"HTML comment openers found: {len(comment_openers)}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
