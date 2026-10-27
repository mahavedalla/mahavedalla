#!/usr/bin/env python3

from pathlib import Path

# 🔧 CHANGE THIS to your desired root directory
ROOT_DIR = Path("/Users/trashboy/Documents/Repositories/mahavedalla/docs/en").resolve()

MAX_MD_FILES = 3  # fewer than 4


def find_bedrock_dirs(root: Path):
    bedrock_dirs = []

    for path in root.rglob("*"):
        if not path.is_dir():
            continue

        entries = list(path.iterdir())

        subdirs = [p for p in entries if p.is_dir()]
        md_files = [p for p in entries if p.is_file() and p.suffix == ".md"]

        # Bedrock: no subdirectories, and fewer than 4 .md files
        if not subdirs and 0 < len(md_files) <= MAX_MD_FILES:
            bedrock_dirs.append((path, len(md_files)))

    return bedrock_dirs


if __name__ == "__main__":
    if not ROOT_DIR.is_dir():
        raise ValueError(f"{ROOT_DIR} is not a valid directory")

    results = find_bedrock_dirs(ROOT_DIR)

    with open("/Users/trashboy/Documents/Repositories/mahavedalla/docs/scripts/md/l4.md", "w") as out_file:
        i = 1
        for d, count in results:
            out_file.write(f"{i}. {d}  ({count} .md files)\n")
            # print(f"{i}. {d}  ({count} .md files)")
            i += 1