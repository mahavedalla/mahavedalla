import os
import re
import unicodedata

def clean(name):
    uni_text = unicodedata.normalize('NFKD', re.sub(r'[!@#$%^&*()?]', '', name)).strip().lower().replace(" ", "-")
    return "".join([c for c in uni_text if not unicodedata.combining(c)])


def sort_files():
    # Get the path of the current directory (sort folder)
    current_dir = "sort"
    
    # Process each .md file in the current directory
    for filename in os.listdir(current_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(current_dir, filename)
            category = None
            
            # Read the file and search for the "Category:" line
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.lower().startswith(" category:"):
                        # Extract the category text after the colon
                        category = clean(line.split(":", 1)[1].strip())
                        print("Category found: ", category)
                        break
            
            if category:
                # Set destination folder to the category name
                dest_folder = os.path.join("questions", category)
                '''
                # Create folder if it does not exist
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                    print(f"Created folder: {dest_folder}")
                
                # Destination file path
                dest_file = os.path.join(dest_folder, filename)
                
                # Move the file
                os.rename(file_path, dest_file)
                print(f"Moved {filename} to folder '{category}'")
            else:
                print(f"No category found in {filename}; skipping.")
                '''
            

if __name__ == "__main__":
    sort_files()

