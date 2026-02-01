import sys
from pathlib import Path

def find_folders_with_many_markdown(directory_path, min_files=10):
    """
    Searches through all subdirectories in a given directory name and 
    returns a list of directory names that contain more than 'min_files' .md files.

    Args:
        directory_path (str or Path): The path to the root directory to search.
        min_files (int): The minimum number of .md files required to return the folder name.

    Returns:
        list: A list of the names (full paths) of the qualifying directories.
    """
    # Ensure the input path is a Path object
    root_dir = Path(directory_path)

    # Check if the root directory actually exists
    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{root_dir}'")
        return []

    qualifying_folders = []

    # Iterate through all items in the directory and its subdirectories (using rglob)
    # The glob pattern '**/', combined with the final glob '*.md', ensures recursive search
    for md_file in root_dir.rglob('*.md'):
        # Get the parent directory of the found .md file
        folder = md_file.parent

        # We use a set to efficiently track which folders have already met the criteria
        # and to count files within a specific folder only once per folder.
        # This approach can be optimized for large numbers of files:
        
        # A more direct approach is to iterate over subdirectories directly
        # and count the files within each:
        pass # The following loop is better for this specific task

    # Better approach: Iterate over subdirectories and check counts
    for subdirectory in root_dir.iterdir():
        if subdirectory.is_dir():
            # Count the number of .md files in the current subdirectory
            # Using glob('*/*.md') gets files only one level deep inside subdirectory
            # We must use the appropriate glob or a generator expression
            
            md_count = sum(1 for f in subdirectory.glob('*.md') if f.is_file())

            if md_count > min_files:
                qualifying_folders.append(str(subdirectory))
                # Optional: print the count for verification
                # print(f"Found {md_count} .md files in {subdirectory.name}")

    return qualifying_folders

folders_found = find_folders_with_many_markdown("/Users/trashboy/Documents/Repositories/mahavedalla/docs/en/question", min_files=15)
i = 1
if folders_found:
    print("The following directories contain more than 15 .md files:")
    for folder in folders_found:
            print(f"{i}. - {folder}")
            i += 1
else:
    print("No qualifying folders found.")


