import os
import re

docs_dir = "."  # adjust if needed

def check(path, out_f):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return  # skip files without wrapped frontmatter

    # find closing ---
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return  # malformed frontmatter

    for i in range(1, end_idx):  # only check frontmatter section
        if re.match(r"^\s*Answer:", lines[i]) or re.match(r"^\s*Answer in Brief:", lines[i]):
            print(f"File detected: {path}")
            out_f.write(f"{path}\n\n")
            break

with open("toclean.md", "a", encoding="utf-8") as out_f:
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                check(os.path.join(root, file), out_f)
