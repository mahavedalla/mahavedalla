import os
import re

docs_dir = "."  # adjust as needed

def clean_sutta_refs(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return  # skip files without frontmatter

    # find closing ---
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return  # malformed frontmatter

    new_lines = []
    changed = False

    for i in range(0, end_idx):
        line = lines[i]
        match = re.match(r"^\s*Sutta References:\s*-\s*$", line)
        if match:
            new_line = "Sutta References:\n"
            new_lines.append(new_line)
            changed = True
            print(f"Cleaned in {path}: {line.strip()} → {new_line.strip()}")
        else:
            new_lines.append(line)

    # add the rest (closing --- + body)
    new_lines.extend(lines[end_idx:])

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Updated {path}")

# Walk through all markdown files
for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            clean_sutta_refs(os.path.join(root, file))
