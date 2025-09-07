import os
import re

docs_dir = "vimutti"  # adjust as needed

def remove_blank_answer_keys(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return  # skip files without frontmatter

    # find closing ---
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return  # malformed frontmatter

    new_lines = [lines[0]]  # opening ---
    changed = False

    for i in range(1, end_idx):
        match = re.match(r"^\s*(Answer|Answer in Brief):\s*(.*)", lines[i])
        if match:
            value = match.group(2).strip()
            if value == "" or value == "-":
                changed = True
                print(f"Removed from {path}: {lines[i].strip()}")
                continue  # skip this line
        new_lines.append(lines[i])

    # closing ---
    new_lines.append(lines[end_idx])
    # remaining content
    new_lines.extend(lines[end_idx + 1:])

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Updated {path}")

# Walk through all markdown files
for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            remove_blank_answer_keys(os.path.join(root, file))
