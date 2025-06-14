import os

def print_tree(start_path, prefix=""):
    ignore = {'.venv', '__pycache__', '.git', '.DS_Store'}

    entries = [e for e in os.listdir(start_path) if e not in ignore]
    entries.sort()

    for i, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(path, prefix + extension)

print_tree(".")
