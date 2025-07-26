import os
# Define the directory containing your Markdown files
docs_dir = "docs/questions"
output_file = os.path.join("docs", "index.md")

def generate_toc():
    toc = "# Table of Contents\n\n"
    for root, _, files in os.walk(docs_dir):
        # Skip hidden directories
        if root.startswith("."):
            continue

        # Get the relative folder name
        folder_name = os.path.relpath(root, docs_dir)
        #if folder_name == ".":
            #folder_name = "Home"

        # Add folder name as a heading
        if folder_name != ".":
            toc += f"## {folder_name.capitalize()}\n\n"

        # Add links to Markdown files in the folder
        for file in sorted(files):
            if file.endswith(".md"):
                file_path = os.path.relpath("questions/" + folder_name + "/" + file)
                # os.path.join(root, file), docs_dir
                #print(file_path)
                file_name = os.path.splitext(file)[0].replace("-", " ").capitalize()
                toc += f"- [{file_name + "?"}]({file_path.replace(' ', '%20')})\n"
        toc += "\n"

    return toc

# Write the TOC to the index.md file
with open(output_file, "w") as f:
    f.write(generate_toc())

print(f"Table of contents generated in {output_file}")