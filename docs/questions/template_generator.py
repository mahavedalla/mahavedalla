import os
from datetime import datetime

# Edit your default metadata here
DEFAULT_METADATA = {
    "Question": "",
    "Category": "",
    "Tags": "",
    "Sutta References": "",
    "Date Entered": datetime.now().strftime("%Y-%m-%d"),
    "Last Revised": datetime.now().strftime("%Y-%m-%d"),
    "Review Status": "Not started",
    "Level": "",
    "Priority": "",
    "Number": "",
    "Draft": "true"
}


TEMPLATE = "---\n" + "\n".join(f"{key}: {value}" for key, value in DEFAULT_METADATA.items()) + "\n---\n\n"

def create_new_entry(filename, directory="questions"):
    if not filename.endswith(".md"):
        filename += ".md"
    filepath = os.path.join(directory, filename)

    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return

    current_directory = os.getcwd()
    print(current_directory)
    with open(filepath, "w") as f:
        f.write(TEMPLATE)
    
    print(f"Created: {filepath}")

# Usage
if __name__ == "__main__":
    new_file = input("Enter new file name (without .md): ").strip()
    create_new_entry(new_file)
