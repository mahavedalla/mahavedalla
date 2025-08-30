import os
import unicodedata
import re

def clean_filename(name):
    uni_text = unicodedata.normalize('NFKD', re.sub(r'[!@#$%^&*()?]', '', name)).strip().lower().replace(" ", "-") + ".md"
    return "".join([c for c in uni_text if not unicodedata.combining(c)])

def change_filename(folder):     

    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            filepath = os.path.join(folder, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()

            # Solo renombrar si empieza con '#'
            if first_line.startswith("#"):

                # Remove "#" and extra spaces
                question = first_line.lstrip("#").strip()

                # Replace illegal charactesrs in filenames
                bad_chars = '<>:"/\\|?*'
                filename = clean_filename(question)

                #print("Filename: ", filename)

                new_filepath = os.path.join(folder, filename)


                
                if not os.path.exists(new_filepath):
                    os.rename(filepath, new_filepath)
                    print(f"Rename: {filename} → {filename}")
                else:
                    print(f"Already exists: {filename}, exiting...")
                
if __name__ == "__main__":
    folder = input("Enter folder name: ")
    if os.path.exists(folder):
        change_filename(folder)
    else:
        print(f"Folder does not exist: {folder}")
