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

    new_lines = []
    changed = False

    for i in range(0, end_idx):
        line = lines[i]
        new_lines.append(line)

        # Insert Tags: if missing and after Category
        if line.strip().startswith("Category:") and "Tags" not in existing_keys:
            new_lines.append("Tags:\n")
            changed = True
            print(f"Added Tags: to {path}")

        # Insert Last Revised: if missing and after Date Entered
        if line.strip().startswith("Date Entered:") and "Last Revised" not in existing_keys:
            new_lines.append("Last Revised:\n")
            changed = True
            print(f"Added Last Revised: to {path}")

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
            ensure_tags_and_last_revised(os.path.join(root, file))
