
from pathlib import Path
import argparse
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
    """Find trailing whitespace on eligible front-matter fields."""
    findings = []
    front_matter_seen = False
    inside_front_matter = False

    with path.open(
        "r", encoding="utf-8-sig", errors="replace", newline=""
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
                "type": "metadata",
                "file": path.relative_to(ROOT).as_posix(),
                "line": line_number,
                "field": field_name,
                "spaces": trailing.count(" "),
                "tabs": trailing.count("\t"),
                "text": line,
            })

    return findings, front_matter_seen


def find_notes_comment_openers(path):
    """Find occurrences of the exact HTML comment opener '<!-- '."""
    findings = []

    with path.open(
        "r", encoding="utf-8-sig", errors="replace", newline=""
    ) as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\r\n")

            if "<!-- " in line:
                findings.append({
                    "type": "comment",
                    "file": path.relative_to(ROOT).as_posix(),
                    "line": line_number,
                    "field": "",
                    "spaces": 0,
                    "tabs": 0,
                    "text": line.strip(),
                })

    return findings


def build_report(files, metadata_findings, comment_findings,
                 files_without_front_matter, sample_mode):
    """Build a Markdown report for the files that were scanned."""
    field_counts = Counter(
        finding["field"] for finding in metadata_findings
    )

    report = [
        "# Metadata Trailing Whitespace Audit",
        "",
        "Read-only audit. No question files were modified.",
        "",
        f"- Scan mode: {'SAMPLE' if sample_mode else 'FULL'}",
        f"- Markdown files scanned: {len(files)}",
        f"- Metadata findings: {len(metadata_findings)}",
        f"- HTML comment opener occurrences: {len(comment_findings)}",
        f"- Files without front matter: {len(files_without_front_matter)}",
        "",
        "## Excluded metadata fields",
        "",
    ]

    report.extend(f"- `{field}`" for field in sorted(EXCLUDED_FIELDS))
    report.extend(["", "## Metadata findings by field", ""])

    if field_counts:
        report.extend([
            "| Field | Lines with trailing whitespace |",
            "|---|---:|",
        ])
        for field, count in sorted(field_counts.items()):
            report.append(f"| `{field}` | {count} |")
    else:
        report.append("No matching metadata whitespace found.")

    report.extend(["", "## Detailed metadata findings", ""])

    if metadata_findings:
        report.extend([
            "| File | Line | Field | Spaces | Tabs |",
            "|---|---:|---|---:|---:|",
        ])
        for finding in metadata_findings:
            report.append(
                f"| `{finding['file']}` | {finding['line']} "
                f"| `{finding['field']}` | {finding['spaces']} "
                f"| {finding['tabs']} |"
            )
    else:
        report.append("No metadata findings.")

    report.extend([
        "",
        "## HTML comment openers (`<!-- `)",
        "",
        f"Occurrences found: {len(comment_findings)}",
        "",
    ])

    if comment_findings:
        report.extend([
            "| File | Line | Matching line |",
            "|---|---:|---|",
        ])
        for finding in comment_findings:
            safe_text = finding["text"].replace("|", "\\|")
            report.append(
                f"| `{finding['file']}` | {finding['line']} "
                f"| `{safe_text}` |"
            )
    else:
        report.append("No exact '<!-- ' openers found.")

    if files_without_front_matter:
        report.extend(["", "## Files without front matter", ""])
        report.extend(
            f"- `{path.relative_to(ROOT).as_posix()}`"
            for path in files_without_front_matter
        )

    return "\n".join(report).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Audit metadata trailing whitespace and HTML comment openers "
            "without modifying question files."
        )
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=20,
        metavar="N",
        help="Show up to N findings in the terminal (default: 20).",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        metavar="N",
        help="Scan only the first N Markdown files, alphabetically.",
    )
    args = parser.parse_args()

    if args.preview < 0:
        parser.error("--preview must be zero or greater.")

    if args.sample is not None and args.sample < 1:
        parser.error("--sample must be at least 1.")

    if not QUESTIONS_DIR.is_dir():
        raise SystemExit(f"Questions directory not found: {QUESTIONS_DIR}")

    all_files = sorted(QUESTIONS_DIR.rglob("*.md"))

    if args.sample is not None:
        files = all_files[:args.sample]
    else:
        files = all_files

    metadata_findings = []
    comment_findings = []
    files_without_front_matter = []

    for path in files:
        findings, has_front_matter = inspect_file(path)
        metadata_findings.extend(findings)

        if not has_front_matter:
            files_without_front_matter.append(path)

        comment_findings.extend(find_notes_comment_openers(path))

    report = build_report(
        files,
        metadata_findings,
        comment_findings,
        files_without_front_matter,
        sample_mode=args.sample is not None,
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    combined = metadata_findings + comment_findings

    print()
    print("AUDIT COMPLETE — no question files were modified.")
    print(f"Scan mode: {'SAMPLE' if args.sample is not None else 'FULL'}")
    print(f"Markdown files scanned: {len(files)}")
    print(f"Metadata findings: {len(metadata_findings)}")
    print(f"HTML comment opener occurrences: {len(comment_findings)}")
    print(f"Files without front matter: {len(files_without_front_matter)}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")

    if combined and args.preview:
        print(f"\nPREVIEW (first {args.preview} findings)")
        print("-" * 60)

        for finding in combined[:args.preview]:
            if finding["type"] == "metadata":
                print(
                    f"[METADATA] {finding['file']}:{finding['line']} "
                    f"field={finding['field']!r}, "
                    f"spaces={finding['spaces']}, tabs={finding['tabs']}"
                )
            else:
                print(
                    f"[COMMENT] {finding['file']}:{finding['line']} "
                    f"{finding['text']}"
                )

        if len(combined) > args.preview:
            print(f"... plus {len(combined) - args.preview} more findings.")

    print("\nNo question files were changed.")


if __name__ == "__main__":
    main()
