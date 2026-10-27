
#!/usr/bin/env python3
"""
Find Markdown files under questions/ whose YAML front matter
contains an Answer: field.

Writes matching file paths to a Markdown report.
Does not modify the question files.
"""

import re
from pathlib import Path


QUESTIONS_DIR = Path("questions")
REPORT_PATH = Path("scripts/md/questions_with_answer_field.md")


def find_front_matter(text):
    """Return the front matter text, or None if absent or malformed."""
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


def main():
    if not QUESTIONS_DIR.is_dir():
        print(f"Error: directory not found: {QUESTIONS_DIR}")
        return 1

    matches = []
    scanned = 0
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

        # Match an Answer: key at the beginning of a YAML line.
        if re.search(r"(?m)^[ \t]*Answer[ \t]*:", front_matter):
            matches.append(path.as_posix())

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Question Files with an Answer Field",
        "",
        "Files under `questions/` whose YAML front matter contains an `Answer:` field.",
        "",
        f"**Markdown files scanned:** {scanned}",
        f"**Matching files:** {len(matches)}",
        "",
    ]

    if matches:
        lines.extend(f"- `{path}`" for path in matches)
    else:
        lines.append("No matching files found.")

    if unreadable:
        lines.extend([
            "",
            "## Files That Could Not Be Read",
            "",
        ])
        lines.extend(
            f"- `{path.as_posix()}` — {reason}"
            for path, reason in unreadable
        )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Markdown files scanned: {scanned}")
    print(f"Files with Answer field: {len(matches)}")
    print(f"Files that could not be read: {len(unreadable)}")
    print(f"Report written to: {REPORT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
