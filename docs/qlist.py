import os
import re
import unicodedata
from pathlib import Path

with open('qlist.md', 'w', encoding='utf-8') as contents_file:
    i = 1
    for root, dirs, files in os.walk('en/questions/dhamma'):
        for file in files:
            if file.endswith('.md'):
                # file_path = os.path.join(root, file)
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    contents = f.read()
                    lines = contents.splitlines()  # Extract question from the second line
                    
                    if len(lines) > 1:
                        question = lines[1][9:]  # Remove the "Question: " prefix
                        contents_file.write(f'{i}. {question}\n\n')
                        i += 1
                    else:
                        print(f"File {file} does not have enough lines to extract question.")