import os

docs_dir = "."  # change this to your docs root

def clean_question(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return

    # Detect "# some text" as first line
    if lines[0].startswith("# "):
        question_text = lines[0].lstrip("#").strip()
        lines[0] = f"Question: {question_text}\n"

        # If the second line is blank, drop it
        if len(lines) > 1 and lines[1].strip() == "":
            lines.pop(1)

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Fixed question in {path}")

for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            clean_question(os.path.join(root, file))
