import sys
import ast
import importlib.util
import configparser
from pathlib import Path
from PyQt6.QtCore import pyqtSignal, QThread
import traceback
import io

from pyflakes.api import check
from pyflakes.reporter import Reporter

class SourceValidator(QThread):
    """Background thread for source validation and safe module loading."""

    validation_complete = pyqtSignal(bool, str, object)  # success, message, module
    preflight_check = pyqtSignal(bool, str)              # success, message
    progress_update = pyqtSignal(int, str)               # progress, message

    def __init__(self, source_path: Path):
        super().__init__()
        self.source_path = source_path
        self.config_path = source_path.parent / f"{source_path.stem}.ini"

    # ----------------- Dependency / Syntax -----------------
    def find_dependencies(self, module_path: Path):
        dependencies = set()
        try:
            content = module_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    dependencies.add(node.module.split('.')[0])
        except Exception as e:
            print(f"[Validator] Dependency parse error: {e}")
        return dependencies

    def is_builtin_module(self, module_name: str) -> bool:
        return module_name in sys.builtin_module_names

    # ----------------- Static Analysis -----------------
    def run_pyflakes_check(self, module_path: Path) -> tuple[bool, str]:
        """Run pyflakes and ignore unused import warnings."""
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            reporter = Reporter(stdout, stderr)

            source = module_path.read_text(encoding="utf-8")
            check(source, str(module_path), reporter)

            output = stdout.getvalue().strip()
            if output:
                formatted = []
                for line in output.splitlines():
                    # Ignore "imported but unused"
                    if "imported but unused" in line:
                        continue
                    # Keep real errors
                    parts = line.split(":", 1)
                    formatted.append(f"[STATIC] {Path(module_path).name}:{parts[1] if len(parts) > 1 else line}")
                if formatted:
                    return False, "\n".join(formatted)
            return True, "Static analysis OK"

        except Exception as e:
            return False, self.format_exception(e, module_path)

    # ----------------- Validation -----------------
    def run(self):
        try:
            self.progress_update.emit(10, "Starting validation...")

            # --- Config ---
            if not self.config_path.exists():
                self.preflight_check.emit(False, f"Missing config: {self.config_path.name}")
                self.validation_complete.emit(False, "Config file missing", None)
                return

            self.progress_update.emit(20, "Reading config...")
            config = configparser.ConfigParser()
            config.read(self.config_path)

            if "source" not in config:
                self.preflight_check.emit(False, "Missing [source] section")
                self.validation_complete.emit(False, "Invalid config", None)
                return

            module_name = config.get("source", "module", fallback=None)
            entry_point = config.get("source", "entry_point", fallback="main_widget")

            if not module_name:
                self.preflight_check.emit(False, "Module not specified")
                self.validation_complete.emit(False, "Missing module name", None)
                return

            # --- Module file ---
            self.progress_update.emit(30, "Checking module file...")
            module_path = self.source_path.parent / f"{module_name}.py"

            if not module_path.exists():
                self.preflight_check.emit(False, f"Missing module file: {module_path.name}")
                self.validation_complete.emit(False, "Module file missing", None)
                return

            # --- Syntax ---
            self.progress_update.emit(40, "Checking syntax...")
            try:
                compile(module_path.read_text(encoding="utf-8"), str(module_path), "exec")
                self.preflight_check.emit(True, "Syntax OK")
            except SyntaxError as e:
                msg = self.format_exception(e, module_path)
                self.preflight_check.emit(False, msg)
                self.validation_complete.emit(False, msg, None)
                return

            # --- Static Analysis ---
            self.progress_update.emit(45, "Running static analysis...")
            ok, msg = self.run_pyflakes_check(module_path)
            if not ok:
                self.preflight_check.emit(False, msg)
                self.validation_complete.emit(False, f"Static analysis failed:\n{msg}", None)
                return

            # --- Dependencies ---
            self.progress_update.emit(55, "Analyzing dependencies...")
            for dep in self.find_dependencies(module_path):
                dep_file = self.source_path.parent / f"{dep}.py"
                if dep_file.exists():
                    self.progress_update.emit(60, f"Found dependency: {dep}")

            # --- Import ---
            self.progress_update.emit(70, "Importing module...")
            module = None
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                try:
                    spec.loader.exec_module(module)
                except ModuleNotFoundError as mnfe:
                    print(f"[Validator] Optional module not found: {mnfe.name}, ignoring.")
                except Exception as e:
                    print(f"[Validator] Runtime error in module '{module_name}':\n", traceback.format_exc())
                    self.preflight_check.emit(False, f"Module runtime error: {e}")
                    self.validation_complete.emit(False, "Module import failed", None)
                    return
            except Exception as e:
                print("[Validator] Import spec error:\n", traceback.format_exc())
                self.preflight_check.emit(False, f"Import spec failed: {e}")
                self.validation_complete.emit(False, "Module import failed", None)
                return

            # --- Entry point ---
            self.progress_update.emit(85, "Checking entry point...")
            if not hasattr(module, entry_point):
                self.preflight_check.emit(False, f"Entry point '{entry_point}' not found")
                self.validation_complete.emit(False, "Entry point missing", None)
                return

            # --- SUCCESS ---
            self.progress_update.emit(100, "Validation complete")
            self.preflight_check.emit(True, "All checks passed")
            self.validation_complete.emit(True, "Source loaded successfully", module)

        except Exception as e:
            print("[Validator] Fatal error:\n", traceback.format_exc())
            self.preflight_check.emit(False, f"Unexpected error: {e}")
            self.validation_complete.emit(False, "Validation crashed", None)

    # ----------------- Exception Formatting -----------------
    def format_exception(self, e: Exception, path: Path | None = None) -> str:
        if isinstance(e, SyntaxError):
            file = Path(e.filename).name if e.filename else (path.name if path else "<?>")
            line = e.lineno or "?"
            col = e.offset or "?"
            text = (e.text or "").rstrip()
            return f"[SYNTAX ERROR] {file}:{line}:{col}\n→ {e.msg}\n→ {text}"

        tb = traceback.extract_tb(e.__traceback__)
        last = tb[-1] if tb else None
        if last:
            return f"[{type(e).__name__}] {Path(last.filename).name}:{last.lineno}\n→ {e}"
        return f"[{type(e).__name__}] {e}"
