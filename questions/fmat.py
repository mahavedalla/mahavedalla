import os
import re

docs_dir = "kamma"  # adjust as needed

def fix_category_key(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return  # skip files without wrapped frontmatter

    # find closing ---
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return  # malformed frontmatter, skip

    changed = False
    for i in range(1, end_idx):  # only scan inside frontmatter
        if re.match(r"^\s+Category:", lines[i]):  # line has leading space before 'Category:'
            fixed = re.sub(r"^\s+Category:", "Category:", lines[i])
            if fixed != lines[i]:
                lines[i] = fixed
                changed = True
                print(f"✨ Fixed leading space in {path}: {fixed.strip()}")

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"✅ Cleaned frontmatter in {path}")

# Walk through all markdown files
for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            fix_category_key(os.path.join(root, file))
