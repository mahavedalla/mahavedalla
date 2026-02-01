#!/usr/bin/env python3

import os
from pathlib import Path

# 🔧 CHANGE THIS to your desired root directory
ROOT_DIR = Path("/Users/trashboy/Documents/Repositories/mahavedalla/docs/en").resolve()


def find_mixed_dirs(root: Path):
    mixed_dirs = []

    for path in root.rglob("*"):
        if not path.is_dir():
            continue

        subdirs = [p for p in path.iterdir() if p.is_dir()]
        md_files = [p for p in path.iterdir() if p.is_file() and p.suffix == ".md"]

        # Must contain BOTH subdirectories and .md files
        if subdirs and md_files:
            mixed_dirs.append(path)

    return mixed_dirs


if __name__ == "__main__":
    if not ROOT_DIR.is_dir():
        raise ValueError(f"{ROOT_DIR} is not a valid directory")

    results = find_mixed_dirs(ROOT_DIR)
    with open("/Users/trashboy/Documents/Repositories/mahavedalla/docs/scripts/md/mixed_dirs.md", "w") as f:
        i = 1
        for d in results:
            f.write(f"{i}: {d}\n")
            i += 1
    for d in results:
        print(d)
