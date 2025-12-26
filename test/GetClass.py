import ast
from pathlib import Path

file_path = Path(
    r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\QtForge Studio\test\ListSample.py"
)

with file_path.open("r", encoding="utf-8") as f:
    tree = ast.parse(f.read())

class_names = [
    node.name
    for node in ast.walk(tree)
    if isinstance(node, ast.ClassDef)
]

print(class_names)
