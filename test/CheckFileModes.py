import os
from pathlib import Path

def get_files_with_extensions(folder_path, extensions=None):
    """
    Recursively scan a folder and return a list of files matching the given extensions.
    Excludes __pycache__ and hidden files.
    """
    if extensions is None:
        extensions = ['.py', '.qss']

    folder = Path(folder_path)
    files_list = []

    for file_path in folder.rglob("*"):  # <-- recursive
        if file_path.is_file():
            # Skip __pycache__ and hidden files
            if file_path.suffix.lower() in extensions and "__pycache__" not in str(file_path):
                files_list.append(str(file_path))

    return files_list


# Example usage
folder_to_scan = r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\QtForge Studio"
files = get_files_with_extensions(folder_to_scan)
print(f"Found {len(files)} files:")
for f in files:
    print(f)
