# libs/stylesheetModefier.py
from PyQt6.QtWidgets import QWidget
from pathlib import Path

class StylesheetModifier:
    def __init__(self, qss_path: str | Path, parent: QWidget):
        self.qss_path = Path(qss_path)
        self.parent = parent

    def apply_stylesheet(self):
        """Load and apply the QSS stylesheet to the parent widget."""
        if not self.qss_path.exists():
            print(f"[StylesheetModifier] QSS file not found: {self.qss_path}")
            return
        try:
            with open(self.qss_path, 'r', encoding='utf-8') as f:
                qss_content = f.read()
                self.parent.setStyleSheet(qss_content)
                print(f"[StylesheetModifier] Stylesheet applied: {self.qss_path.name}")
        except Exception as e:
            print(f"[StylesheetModifier] Failed to apply stylesheet: {e}")
