
from pathlib import Path
import csv
import re
import sys


def audit_file(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    issues = []

    if not text.strip():
        return ["Blank file"]

    start = re.match(r"\A---[ \t]*\r?\n", text)

    if not start:
        issues.append("Missing front matter")
        body = text
    else:
        remainder = text[start.end():]
        closing = re.search(r"(?m)^---[ \t]*\r?$", remainder)

        if not closing:
            return ["Unclosed front matter"]

        body = remainder[closing.end():]

        if not body.strip():
            issues.append("Front matter only")

    if not re.search(r"(?m)^\s*\*\*#\s+.+?\*\*\s*$", body):
        issues.append("Missing question heading")

    if not re.search(
        r"(?m)^\s*\*\*##\s+Bibliography\s*\*\*\s*$", body
    ):
        issues.append("Missing bibliography heading")

    has_notes = (
        "<!--" in body
        and re.search(r"(?m)^\s*Notes\s*:", body) is not None
        and "-->" in body
    )

    if not has_notes:
        issues.append("Missing or incomplete notes block")

    return issues


def main():
    root = Path(__file__).resolve().parents[3]
    scan_dir = root / "docs" / "en"
    report = root / "markdown_structure_report.csv"
    notes_report = root / "missing_notes_report.md"

    if not scan_dir.is_dir():
        sys.exit(f"Error: scan directory does not exist: {scan_dir}")

    files = sorted(scan_dir.rglob("*.md"))
    findings = []
    counts = {}

    for path in files:
        try:
            issues = audit_file(path)
        except OSError as exc:
            issues = [f"Read error: {exc}"]

        if issues:
            findings.append({
                "File": path.relative_to(root).as_posix(),
                "Issues": "; ".join(issues),
            })

            for issue in issues:
                counts[issue] = counts.get(issue, 0) + 1

    # Write the complete CSV report.
    with report.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["File", "Issues"])
        writer.writeheader()
        writer.writerows(findings)

    # Write a separate Markdown report for files flagged for missing notes.
    missing_notes = [
        item["File"]
        for item in findings
        if "Missing or incomplete notes block" in item["Issues"]
    ]

    with notes_report.open("w", encoding="utf-8") as f:
        f.write("# Files flagged for missing or incomplete notes\n\n")

        for path in missing_notes:
            f.write(f"- `{path}`\n")

    print(f"Scan directory: {scan_dir}")
    print(f"Markdown files scanned: {len(files)}")
    print(f"Files with findings: {len(findings)}")
    print(f"Files without detected issues: {len(files) - len(findings)}")
    print("\nFindings by issue (counts may overlap):")

    for issue, count in sorted(counts.items()):
        print(f"  {issue}: {count}")

    print(f"\nCSV report written to: {report}")
    print(f"Missing-notes report written to: {notes_report}")
    print(f"Files flagged for missing notes: {len(missing_notes)}")


if __name__ == "__main__":
    main()
