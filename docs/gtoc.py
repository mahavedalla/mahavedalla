import os
import yaml

ROOT_DIR = "questions"   # questions inside docs
OUTPUT_FILE = "questions/toc.md"   # toc.md inside docs
CATEGORIES = "cat.md"

toc = {}
cat = []

def get_frontmatter(md_path):
    """Return the frontmatter as a dict, or None if none exists."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return None

    frontmatter_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        frontmatter_lines.append(line)

    try:
        return yaml.safe_load("".join(frontmatter_lines))
    except Exception:
        return None

# Walk through the questions directory
for root, dirs, files in os.walk(ROOT_DIR):
    rel_path = os.path.relpath(root, ROOT_DIR)
    if rel_path == ".":
        continue

    # Determine category name from frontmatter
    category = None
    for file in files:
        if file.endswith(".md"):
            fm = get_frontmatter(os.path.join(root, file))
            if fm and "Category" in fm:
                category = fm["Category"]
                break

    if not category:
        category = rel_path.split(os.sep)[0]

    if category not in toc:
        toc[category] = []
    
    if category not in cat:
        cat.append(category)

    for file in files:
        if file.endswith(".md"):
            full_path = os.path.join(root, file)
            fm = get_frontmatter(full_path)
            question = fm.get("Question") if fm else None
            if question:
                # Path relative to toc.md inside docs/
                rel_file_path = os.path.relpath(full_path, os.path.dirname(OUTPUT_FILE))
                rel_file_path = rel_file_path.replace(os.sep, "/")  # forward slashes for VS Code
                toc[category].append((question, rel_file_path))

# Write TOC
# inside the write loop
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for category, items in toc.items():
        f.write(f"## {category}\n\n")
        for title, path in sorted(items):
            # wrap path in angle brackets to handle spaces/special chars
            f.write(f"- [{title}](<{path}>)\n")
        f.write("\n")

print(f"Table of contents written to {OUTPUT_FILE}")

with open(CATEGORIES, "w", encoding="utf-8") as f:
    for c in sorted(cat):
        f.write(f"- {c}\n")

# print(cat)
