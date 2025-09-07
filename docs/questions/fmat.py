import os
import re

docs_dir = "vamsa"  # adjust if needed

def fix_category_key(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return  # skip files without wrapped frontmatter

    # find closing ---
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return  # malformed frontmatter

    changed = False
    for i in range(1, end_idx):  # only check frontmatter section
        if re.match(r"^\s+Category:", lines[i]):
            fixed = re.sub(r"^\s+Category:", "Category:", lines[i])
            if fixed != lines[i]:
                print(f"  ✨ Fixed in {path}: {lines[i].strip()} → {fixed.strip()}")
                lines[i] = fixed
                changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"✅ Cleaned Category key in {path}")

for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            fix_category_key(os.path.join(root, file))
