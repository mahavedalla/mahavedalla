import os

docs_dir = "questions"  # adjust if needed

def ensure_tags_and_last_revised(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return  # skip files without frontmatter

    # find closing ---
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return  # malformed frontmatter

    # track existing keys
    existing_keys = {line.split(":", 1)[0].strip() for line in lines[1:end_idx] if ":" in line}

    if existing_keys.

# Walk through all markdown files
for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            ensure_tags_and_last_revised(os.path.join(root, file))
