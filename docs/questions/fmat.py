import os
import re

docs_dir = "."  # current folder (questions/)

def clean_frontmatter(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return

    # Skip if file already starts with ---
    if lines[0].strip() == "---":
        return

    # Detect metadata block at top (lines like key: value)
    meta_block = []
    for line in lines:
        if re.match(r"^\s*\w+\s*:\s*.+", line):  # matches "key: value"
            meta_block.append(line)
        else:
            break

    if meta_block:
        # Wrap the metadata block with ---
        new_lines = ["---\n"] + meta_block + ["---\n"] + lines[len(meta_block):]
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Wrapped frontmatter in {path}")

for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            clean_frontmatter(os.path.join(root, file))
