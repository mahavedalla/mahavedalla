
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_DIR = ROOT / "questions"
REPORT_PATH = ROOT / "scripts" / "md" / "trailing_whitespace_report.md"

TRAILING_WHITESPACE = re.compile(r"[ \t]+$")


def inspect_file(path):
    """Return trailing-whitespace findings without changing the file."""
    findings = []

    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            # Remove only the line-ending characters for inspection.
            line = raw_line.rstrip("\r\n")
            match = TRAILING_WHITESPACE.search(line)

            if not match:
                continue

            whitespace = match.group()
            content = line[:match.start()]

            if not content:
                kind = "Whitespace on blank line"
            elif len(whitespace) >= 2 and set(whitespace) == {" "}:
                kind = "Possible intentional Markdown line break"
            elif "\t" in whitespace:
                kind = "Trailing tab or mixed whitespace"
            else:
                kind = "Trailing space"

            findings.append({
                "line": line_number,
                "kind": kind,
                "count": len(whitespace),
                "whitespace": whitespace.replace(" ", "space").replace("\t", "tab"),
            })

    return findings


def main():
    if not QUESTIONS_DIR.is_dir():
        raise SystemExit(f"Questions directory not found: {QUESTIONS_DIR}")

    files = sorted(QUESTIONS_DIR.rglob("*.md"))
    report_lines = [
        "# Trailing Whitespace Audit",
        "",
        "This report is read-only: no question files were modified.",
        "",
        f"- Directory scanned: `{QUESTIONS_DIR.relative_to(ROOT)}`",
        f"- Markdown files scanned: {len(files)}",
        "",
        "## Summary",
        "",
    ]

    affected_files = 0
    total_findings = 0
    total_blank_lines = 0
    total_hard_break_candidates = 0
    total_tabs = 0

    detailed_results = []

    for path in files:
        findings = inspect_file(path)
        if not findings:
            continue

        affected_files += 1
        total_findings += len(findings)

        for finding in findings:
            if finding["kind"] == "Whitespace on blank line":
                total_blank_lines += 1
            elif finding["kind"] == "Possible intentional Markdown line break":
                total_hard_break_candidates += 1
            if "tab" in finding["whitespace"]:
                total_tabs += 1

        detailed_results.append((path, findings))

    report_lines.extend([
        f"- Files with trailing whitespace: {affected_files}",
        f"- Lines with trailing whitespace: {total_findings}",
        f"- Blank lines with whitespace: {total_blank_lines}",
        f"- Possible intentional Markdown line breaks: {total_hard_break_candidates}",
        f"- Lines with trailing tabs: {total_tabs}",
        "",
        "## Findings",
        "",
    ])

    if not detailed_results:
        report_lines.append("No trailing spaces or tabs found.")
    else:
        for path, findings in detailed_results:
            relative_path = path.relative_to(ROOT).as_posix()
            report_lines.extend([
                f"### `{relative_path}`",
                "",
                "| Line | Finding | Trailing characters |",
                "|---:|---|---|",
            ])

            for finding in findings:
                report_lines.append(
                    f"| {finding['line']} | {finding['kind']} "
                    f"| {finding['count']} ({finding['whitespace']}) |"
                )

            report_lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(report_lines).rstrip() + "\n",
        encoding="utf-8",
    )

    print("Audit complete. No question files were modified.")
    print(f"Markdown files scanned: {len(files)}")
    print(f"Files with trailing whitespace: {affected_files}")
    print(f"Lines with trailing whitespace: {total_findings}")
    print(f"Report saved to: {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
