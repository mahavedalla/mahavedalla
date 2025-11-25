import os
from collections import defaultdict

def find_duplicates():
    questions_dir = "questions"
    filenames = defaultdict(list)
    
    # Walk through all subdirectories and collect filenames
    for root, _, files in os.walk(questions_dir):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                filenames[file].append(full_path)
    
    # Write duplicates to markdown file
    output_file = "duplicates.md"
    with open(output_file, "w") as f:
        f.write("# Duplicate Filenames\n\n")
        
        duplicates_found = False
        for filename, paths in sorted(filenames.items()):
            if len(paths) > 1:
                duplicates_found = True
                f.write(f"## {filename} ({len(paths)} copies)\n\n")
                for path in sorted(paths):
                    f.write(f"- {path}\n")
                f.write("\n")
        
        if not duplicates_found:
            f.write("No duplicate filenames found.\n")
    
    print(f"Duplicates written to {output_file}")

if __name__ == "__main__":
    find_duplicates()