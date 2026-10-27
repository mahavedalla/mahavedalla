# ...existing code...
import os

# set ROOT to the docs directory (file is already inside docs/)
ROOT = os.path.abspath(os.path.dirname(__file__))  # docs/
SEARCH_DIR = os.path.join(ROOT, "questions")
OUTPUT = os.path.join(ROOT, "1d8_files.md")
PATTERN = "1d8"

def main():
    matches = []
    for root, _, files in os.walk(SEARCH_DIR):
        for fn in files:
            if fn.endswith(".md") and PATTERN in fn:
                rel = os.path.relpath(os.path.join(root, fn), ROOT).replace("\\", "/")
                matches.append(rel)

    with open(OUTPUT, "w", encoding="utf-8") as out:
        out.write("# Files containing '1d8' in the filename\n\n")
        if matches:
            i = 1
            for p in sorted(matches):
                out.write(f"{i}. [{os.path.basename(p)}]({p})\n\n")
                i += 1
        else:
            out.write("No matching files found.\n")

    print(f"Wrote {len(matches)} entries to {OUTPUT}")

if __name__ == "__main__":
    main()
# ...existing code...