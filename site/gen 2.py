import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

# Default metadata for the new entry
# Automatically set the date fields to the current date and review status to "Not started"

def create_new_entry(filename, question, category, directory="questions"):
    
    # The raw template string with placeholders for metadata
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
    "Draft": "true"
    }

    TEMPLATE = "---\n" + "\n".join(f"{key}: {value}" for key, value in DEFAULT_METADATA.items()) + "\n---\n\n"

    # Update file name based on directory
    if directory != "questions":
        filename = os.path.join(directory, filename)
    
    if os.path.exists(filename):
        print(f"File already exists: {filename}")
        return

    # Write the template to the new file
    with open(filename, "w") as f:
        f.write(TEMPLATE + "# " + question + "\n\n## Bibliography\n\n<!-- \n\nNotes:\n\n\n\n-->")

# Function to clean and format the filename (removing special characters and diacritics)    
def clean_filename(name):
    uni_text = unicodedata.normalize('NFKD', re.sub(r'[!@#$%^&*()?,]', '', name)).strip().lower().replace(" ", "-") + ".md"
    return "".join([c for c in uni_text if not unicodedata.combining(c)])

def find_category_path(category: str) -> Path:
    """
    Search recursively under QUESTIONS_ROOT for a directory whose name matches category.
    Returns the full Path if found, raises FileNotFoundError otherwise.
    """
    for path in Path("questions").rglob("*"):  # recursive search
        if path.is_dir() and path.name == category:
            return path
    return None

# Usage
if __name__ == "__main__":
    # Needed Updates
    # none
  
    # Receive user input for file name and directory
    question = input("Enter new question: ")
    filename = clean_filename(question)
    category = input("Category: ") or "questions"

    # Format directory name based on category
    strcat = "".join([c for c in unicodedata.normalize('NFKD', category).strip().lower() if not unicodedata.combining(c)])
    directory = find_category_path(strcat)
    if directory is None:
        directory = "questions/" + strcat
        os.makedirs(directory)
        print(f"Category directory not found. Created new directory: {directory}")
    else: 
        print(f"Found category directory: {directory}")

    # Create directory if it doesn't exist
    '''
    if not os.path.exists(directory):
        print(f"Directory does not exist. Making directory: {directory}")
        os.makedirs(directory)
    '''
    
    # Create new entry if file name is provided
    if filename == "":
        print("No file name provided. Exiting.")
    else:
        if directory != "":
            create_new_entry(filename, question, category, directory=directory)
        else:
            create_new_entry(filename, question, category)