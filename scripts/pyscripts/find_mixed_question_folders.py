
#!/usr/bin/env python3
"""
Identify folders under questions/ that contain both:
- one or more Markdown files
- one or more immediate subfolders

Writes the results to a Markdown report.
Does not modify question files.
"""

from pathlib import Path


QUESTIONS_DIR = Path("questions")
REPORT_PATH = Path("scripts/md/mixed_question_folders.md")


def main():
    if not QUESTIONS_DIR.is_dir():
        print(f"Error: directory not found: {QUESTIONS_DIR}")
        return 1

    mixed_folders = []

    # Include questions/ itself and every folder beneath it.
    folders = [QUESTIONS_DIR]
    folders.extend(
        path for path in QUESTIONS_DIR.rglob("*")
        if path.is_dir()
    )

    for folder in folders:
        try:
            children = list(folder.iterdir())
        except OSError as exc:
            print(f"Warning: cannot read {folder}: {exc}")
            continue

        has_markdown = any(
            child.is_file() and child.suffix.lower() == ".md"
            for child in children
        )

        has_subfolders = any(
            child.is_dir()
            for child in children
        )

        if has_markdown and has_subfolders:
            mixed_folders.append(folder)

    # Sort paths for a predictable report.
    mixed_folders.sort(key=lambda path: path.as_posix().lower())

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Mixed Folders in questions/",
        "",
        "Folders containing both direct Markdown files and subfolders.",
        "",
        f"**Total mixed folders: {len(mixed_folders)}**",
        "",
    ]

    if mixed_folders:
        for folder in mixed_folders:
            lines.append(f"- `{folder.as_posix()}`")
    else:
        lines.append("No mixed folders found.")

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(f"Folders examined: {len(folders)}")
    print(f"Mixed folders found: {len(mixed_folders)}")
    print(f"Report written to: {REPORT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
