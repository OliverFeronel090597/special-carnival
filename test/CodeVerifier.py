from pyflakes.api import check
from pyflakes.reporter import Reporter
import io
from pathlib import Path

def check_file_pyflakes(file_path: Path):
    output = io.StringIO()
    error = io.StringIO()
    reporter = Reporter(output, error)
    
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()
    
    # Returns 0 if no errors, non-zero otherwise
    result = check(source_code, str(file_path), reporter)
    
    output_text = output.getvalue()
    error_text = error.getvalue()
    
    if result == 0:
        print(f"[OK] {file_path} passed pyflakes check")
    else:
        print(f"[Errors] {file_path}:")
        print(output_text)
        if error_text:
            print(error_text)
    
    return result == 0

# Example usage:
if __name__ == "__main__":
    from pathlib import Path
    check_file_pyflakes(Path("RandomBals.py"))
