
#!/usr/bin/env python3
"""
Find question Markdown files whose Date Entered or Last Revised
front matter values do not match MM/DD/YY.

Writes file paths and problematic values to a Markdown report.
Does not modify source files.
"""

import re
from pathlib import Path


QUESTIONS_DIR = Path("questions")
REPORT_PATH = Path("scripts/md/nonstandard_front_matter_dates.md")

DATE_FIELDS = ("Date Entered", "Last Revised")
EXPECTED_DATE = re.compile(r"^\d{2}/\d{2}/\d{2}$")


def find_front_matter(text):
    """Return front matter text, or None if absent or malformed."""
    if text.startswith("\ufeff"):
        text = text[1:]

    opening = re.match(r"---[ \t]*(?:\r\n|\n|\r|$)", text)
    if not opening:
        return None

    closing = re.search(
        r"(?m)^---[ \t]*(?:\r\n|\n|\r|$)",
        text[opening.end():],
    )

    if not closing:
        return None

    return text[opening.end():opening.end() + closing.start()]


def inspect_dates(front_matter):
    """Return date fields that are missing, blank, or nonstandard."""
    values = {}

    for line in front_matter.splitlines():
        match = re.match(
            r"^[ \t]*(Date Entered|Last Revised)[ \t]*:[ \t]*(.*?)[ \t]*$",
            line,
        )
        if match:
            field = match.group(1)
            value = match.group(2).strip()
            values.setdefault(field, []).append(value)

    problems = []

    for field in DATE_FIELDS:
        field_values = values.get(field, [])

        if not field_values:
            problems.append((field, "MISSING"))
            continue

        if len(field_values) > 1:
            problems.append((field, "DUPLICATE FIELD"))
            continue

        value = field_values[0]

        if not value:
            problems.append((field, "BLANK"))
        elif not EXPECTED_DATE.fullmatch(value):
            problems.append((field, value))

    return problems


def main():
    if not QUESTIONS_DIR.is_dir():
        print(f"Error: directory not found: {QUESTIONS_DIR}")
        return 1

    scanned = 0
    matches = []
    unreadable = []

    for path in sorted(QUESTIONS_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() != ".md":
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            unreadable.append((path, str(exc)))
            continue

        scanned += 1
        front_matter = find_front_matter(text)

        if front_matter is None:
            continue

        problems = inspect_dates(front_matter)

        if problems:
            matches.append((path.as_posix(), problems))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Nonstandard Front Matter Dates",
        "",
        "Expected format: `MM/DD/YY`.",
        "Fields checked: `Date Entered` and `Last Revised`.",
        "",
        f"**Markdown files scanned:** {scanned}",
        f"**Files needing review:** {len(matches)}",
        "",
    ]

    if matches:
        for path, problems in matches:
            lines.append(f"## `{path}`")
            for field, value in problems:
                lines.append(f"- **{field}:** `{value}`")
            lines.append("")
    else:
        lines.append("No files needing review were found.")

    if unreadable:
        lines.extend([
            "## Files That Could Not Be Read",
            "",
        ])
        for path, reason in unreadable:
            lines.append(f"- `{path.as_posix()}` — {reason}")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Markdown files scanned: {scanned}")
    print(f"Files needing review: {len(matches)}")
    print(f"Files that could not be read: {len(unreadable)}")
    print(f"Report written to: {REPORT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
