import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path


def create_new_entry(filename, question, category, directory: Path):
    DEFAULT_METADATA = {
        "Question": question,
        "Category": category,
        "Tags": "",
        "Sutta References": "",
        "Date Entered": datetime.now().strftime("%-m-%-d-%y"),
        "Last Revised": datetime.now().strftime("%-m-%-d-%y"),
        "Review Status": "Not started",
        "Level": "",
        "Priority": "",
        "Number": "",
        "Draft": "true",
    }

    TEMPLATE = "---\n" + "\n".join(f"{key}: {value}" for key, value in DEFAULT_METADATA.items()) + "\n---\n\n"

    filename = Path(filename)

    if filename.exists():
        print(f"File already exists: {filename}")
        return

    # Ensure output directory exists
    directory.mkdir(parents=True, exist_ok=True)

    with filename.open("w", encoding="utf-8") as f:
        f.write(TEMPLATE + "# " + question + "\n\n## Bibliography\n\n<!-- \n\nNotes:\n\n\n\n-->")

def clean_filename(name):
    uni_text = unicodedata.normalize(
        "NFKD",
        re.sub(r"[!@#$%^&*()?,']", "", name),
    ).strip().lower().replace(" ", "-") + ".md"
    return "".join([c for c in uni_text if not unicodedata.combining(c)])

if __name__ == "__main__":
    question = input("Enter new question: ")
    category = input("Category: ") or "questions"

    # Assumption: your target folder is at:
    # docs/en/questions/dhamma/sort relative to the repo root.
    repo_root = Path(__file__).resolve().parents[2]  # adjust if your script is not one level below repo root
    directory = repo_root / "en" / "questions" / "dhamma" / "sort"

    out_file = directory / clean_filename(question)

    if not question:
        print("No file name provided. Exiting.")
    else:
        create_new_entry(out_file, question, category, directory)
