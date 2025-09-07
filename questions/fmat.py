import os

docs_dir = "."  # adjust as needed

REQUIRED_KEYS = {
    "Level": "",
    "Priority": "",
    "Number": "",
    "Draft": "true"
}

def ensure_required_keys(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return  # skip files without frontmatter

    # find closing ---
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return  # malformed frontmatter

    # collect existing keys
    existing_keys = set()
    for i in range(1, end_idx):
        if ":" in lines[i]:
            key = lines[i].split(":", 1)[0].strip()
            existing_keys.add(key)

    # add missing keys before closing ---
    new_lines = lines[:end_idx]
    changed = False
    for key, default in REQUIRED_KEYS.items():
        if key not in existing_keys:
            new_line = f"{key}: {default}\n"
            new_lines.append(new_line)
            changed = True
            print(f"Added to {path}: {new_line.strip()}")

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
            ensure_required_keys(os.path.join(root, file))
