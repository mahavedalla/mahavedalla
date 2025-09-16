import os
import yaml

# Root directory containing your categories
ROOT_DIR = "questions"

toc = {}

def get_frontmatter_question(md_path):
    """Return the 'question' from the frontmatter if available, else None."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if lines[0].strip() == "---":
        # frontmatter exists
        frontmatter_lines = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            frontmatter_lines.append(line)
        try:
            data = yaml.safe_load("".join(frontmatter_lines))
            return data.get("question")
        except Exception:
            return None
    return None

for root, dirs, files in os.walk(ROOT_DIR):
    # Determine category as the top-level directory relative to ROOT_DIR
    rel_path = os.path.relpath(root, ROOT_DIR)
    if rel_path == ".":
        continue
    category = rel_path.split(os.sep)[0]

    if category not in toc:
        toc[category] = []

    for file in files:
        if file.endswith(".md"):
            full_path = os.path.join(root, file)
            title = get_frontmatter_question(full_path) or os.path.splitext(file)[0]
            # Store path relative to ROOT_DIR
            rel_file_path = os.path.relpath(full_path, ROOT_DIR)
            toc[category].append((title, rel_file_path))

# Generate Markdown TOC
for category, items in toc.items():
    print(f"## {category}\n")
    for title, path in sorted(items):
        print(f"- [{title}]({path})")
    print("\n")
