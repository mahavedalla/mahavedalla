import os
import re

docs_dir = "."  # adjust if needed

def wrap_missing_frontmatter(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return

    # Case 1: Already wrapped
    if lines[0].strip() == "---":
        return

    # Case 2: Starts with key: value style frontmatter (unwrapped)
    if re.match(r"^\s*[\w\s]+:\s*.+", lines[0]):
        # find the first blank line (end of metadata)
        idx = None
        for i, line in enumerate(lines):
            if not line.strip():  # blank line
                idx = i
                break

        if idx is None:
            idx = len(lines)  # fallback: all lines are metadata

        # ensure newline before closing ---
        if not lines[idx - 1].endswith("\n"):
            lines[idx - 1] += "\n"

        # add wrapping
        new_lines = ["---\n"] + lines[:idx] + ["---\n"] + lines[idx:]

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        
        print(f"✅ Wrapped missing frontmatter in {path} (closing --- at line {idx+1})")


for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            wrap_missing_frontmatter(os.path.join(root, file))
