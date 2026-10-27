
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


def split_line_ending(raw_line):
    """Separate a line's content from its original line ending."""
    if raw_line.endswith("\r\n"):
        return raw_line[:-2], "\r\n"
    if raw_line.endswith("\n") or raw_line.endswith("\r"):
        return raw_line[:-1], raw_line[-1:]
    return raw_line, ""


def inspect_file(path, apply_changes=False):
    """
    Inspect metadata trailing whitespace.

    If apply_changes is True, remove trailing spaces and tabs only from
    eligible front-matter fields. Preserve line endings and all other text.
    """
    with path.open(
        "r", encoding="utf-8-sig", errors="replace", newline=""
    ) as handle:
        original_lines = handle.readlines()

    updated_lines = original_lines.copy()
    findings = []
    inside_front_matter = False
    front_matter_seen = False
    changed = False

    for index, raw_line in enumerate(original_lines):
        line, eol = split_line_ending(raw_line)
        line_number = index + 1

        if index == 0 and line.strip() == "---":
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
            "file": path.relative_to(ROOT).as_posix(),
            "line": line_number,
            "field": field_name,
            "spaces": trailing.count(" "),
            "tabs": trailing.count("\t"),
            "text": line,
        })

        if apply_changes:
            cleaned_line = line[:whitespace_match.start()]
            updated_lines[index] = cleaned_line + eol
            changed = True

    if apply_changes and changed:
        with path.open(
            "w", encoding="utf-8-sig", newline=""
        ) as handle:
            handle.writelines(updated_lines)

    status = (
        "UPDATED" if apply_changes and changed
        else "WOULD UPDATE" if findings
        else "UNCHANGED"
    )

    return findings, front_matter_seen, status


def find_notes_comment_openers(path):
    """Report exact '<!-- ' occurrences without changing them."""
    findings = []

    with path.open(
        "r", encoding="utf-8-sig", errors="replace", newline=""
    ) as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line, _ = split_line_ending(raw_line)

            if "<!-- " in line:
                findings.append({
                    "file": path.relative_to(ROOT).as_posix(),
                    "line": line_number,
                    "text": line,
                })

    return findings


def build_report(
    files,
    file_statuses,
    metadata_findings,
    comment_findings,
    files_without_front_matter,
    mode,
):
    """Build the Markdown audit and update report."""
    field_counts = Counter(
        finding["field"] for finding in metadata_findings
    )

    updated_count = sum(
        status == "UPDATED" for _, status in file_statuses
    )
    would_update_count = sum(
        status == "WOULD UPDATE" for _, status in file_statuses
    )
    unchanged_count = sum(
        status == "UNCHANGED" for _, status in file_statuses
    )

    report = [
        "# Metadata Trailing Whitespace Audit",
        "",
        "Targeted metadata cleanup report.",
        "",
        f"- Mode: {mode}",
        f"- Markdown files inspected: {len(files)}",
        f"- Metadata whitespace findings: {len(metadata_findings)}",
        f"- Files updated: {updated_count}",
        f"- Files that would be updated: {would_update_count}",
        f"- Files unchanged: {unchanged_count}",
        f"- HTML comment opener occurrences (`<!-- `): "
        f"{len(comment_findings)}",
        f"- Files without front matter: "
        f"{len(files_without_front_matter)}",
        "",
        "## File statuses",
        "",
        "| Status | File |",
        "|---|---|",
    ]

    for path, status in file_statuses:
        report.append(
            f"| **{status}** | "
            f"`{path.relative_to(ROOT).as_posix()}` |"
        )

    report.extend(["", "## Excluded metadata fields", ""])
    report.extend(f"- `{field}`" for field in sorted(EXCLUDED_FIELDS))

    report.extend(["", "## Metadata findings by field", ""])

    if field_counts:
        report.extend([
            "| Field | Findings |",
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
        "These occurrences are reported only. They are not modified.",
        "",
    ])

    if comment_findings:
        report.extend([
            "| File | Line | Matching text |",
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

    report.extend([
        "",
        "## Cleanup scope",
        "",
        "- Only trailing spaces or tabs on eligible front-matter "
        "metadata lines are removed.",
        "- Excluded fields are not modified.",
        "- Markdown body content is not modified.",
        "- HTML comment opener spacing is not modified.",
        "- Original line endings are preserved.",
        "",
    ])

    return "\n".join(report).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Audit or clean trailing whitespace on selected metadata "
            "fields. HTML comment openers are report-only."
        )
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--sample",
        type=int,
        metavar="N",
        help="Audit the first N Markdown files without modifying them.",
    )
    mode_group.add_argument(
        "--apply-sample",
        type=int,
        metavar="N",
        help="Clean the first N Markdown files alphabetically.",
    )
    mode_group.add_argument(
        "--apply",
        action="store_true",
        help="Clean all Markdown files.",
    )

    parser.add_argument(
        "--preview",
        type=int,
        default=20,
        metavar="N",
        help="Show up to N findings in the terminal (default: 20).",
    )

    args = parser.parse_args()

    if args.preview < 0:
        parser.error("--preview must be zero or greater.")

    if args.sample is not None and args.sample < 1:
        parser.error("--sample must be at least 1.")

    if args.apply_sample is not None and args.apply_sample < 1:
        parser.error("--apply-sample must be at least 1.")

    if not QUESTIONS_DIR.is_dir():
        raise SystemExit(f"Questions directory not found: {QUESTIONS_DIR}")

    all_files = sorted(QUESTIONS_DIR.rglob("*.md"))

    if args.sample is not None:
        files = all_files[:args.sample]
        apply_changes = False
        mode = f"AUDIT SAMPLE ({len(files)} files)"
    elif args.apply_sample is not None:
        files = all_files[:args.apply_sample]
        apply_changes = True
        mode = f"APPLY SAMPLE ({len(files)} files)"
    else:
        files = all_files
        apply_changes = args.apply
        mode = "APPLY FULL" if apply_changes else "AUDIT FULL"

    file_statuses = []
    metadata_findings = []
    comment_findings = []
    files_without_front_matter = []

    for path in files:
        findings, has_front_matter, status = inspect_file(
            path, apply_changes=apply_changes
        )
        metadata_findings.extend(findings)
        file_statuses.append((path, status))

        if not has_front_matter:
            files_without_front_matter.append(path)

        comment_findings.extend(find_notes_comment_openers(path))

    report = build_report(
        files,
        file_statuses,
        metadata_findings,
        comment_findings,
        files_without_front_matter,
        mode,
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    updated_count = sum(
        status == "UPDATED" for _, status in file_statuses
    )
    would_update_count = sum(
        status == "WOULD UPDATE" for _, status in file_statuses
    )
    unchanged_count = sum(
        status == "UNCHANGED" for _, status in file_statuses
    )

    print()
    print("AUDIT COMPLETE")
    print(f"Mode: {mode}")
    print(f"Markdown files inspected: {len(files)}")
    print(f"Metadata whitespace findings: {len(metadata_findings)}")
    print(f"Files updated: {updated_count}")
    print(f"Files that would be updated: {would_update_count}")
    print(f"Files unchanged: {unchanged_count}")
    print(f"HTML comment opener occurrences: {len(comment_findings)}")
    print(f"Files without front matter: {len(files_without_front_matter)}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")

    if metadata_findings and args.preview:
        print(f"\nPREVIEW (first {args.preview} metadata findings)")
        print("-" * 60)

        for finding in metadata_findings[:args.preview]:
            print(
                f"{finding['file']}:{finding['line']} "
                f"field={finding['field']!r}, "
                f"spaces={finding['spaces']}, tabs={finding['tabs']}"
            )

        if len(metadata_findings) > args.preview:
            print(
                f"... plus {len(metadata_findings) - args.preview} "
                "more metadata findings."
            )

    print("\nHTML comment opener spacing was not changed.")


if __name__ == "__main__":
    main()
