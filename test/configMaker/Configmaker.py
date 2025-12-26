from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QMessageBox,
    QInputDialog, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt
import sys
from pathlib import Path
import ast

# TEMP only – fix your project structure later
sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.stylesheetModefier import StylesheetModifier


class ConfigMaker(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Config Maker")
        self.setGeometry(100, 100, 800, 600)
        self.setObjectName("ConfigMakerRoot")

        self.current_source: Path | None = None
        self.entry_point: str | None = None

        self._build_ui()
        self._connect_signals()
        self._apply_styles()

    # ---------- UI ----------

    def _build_ui(self):
        # Root layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)

        # ---------- Top action bar ----------
        self.action_bar = QFrame()
        self.action_bar.setObjectName("ActionBar")

        action_layout = QHBoxLayout(self.action_bar)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)

        self.select_file_btn = QPushButton("📎 Select Python File")
        self.select_file_btn.setObjectName("SelectFileButton")

        self.save_btn = QPushButton("💾 Save Config")
        self.save_btn.setObjectName("SaveConfigButton")
        self.save_btn.setEnabled(False)

        action_layout.addWidget(self.select_file_btn)
        action_layout.addStretch()              # pushes Save to the right
        action_layout.addWidget(self.save_btn)

        self.main_layout.addWidget(self.action_bar)

        # ---------- Config preview ----------
        self.config_text = QTextEdit()
        self.config_text.setObjectName("ConfigTextEdit")
        self.config_text.setReadOnly(True)
        self.config_text.setPlaceholderText("Generated .ini configuration preview…")

        self.main_layout.addWidget(self.config_text, stretch=1)

    def _connect_signals(self):
        self.select_file_btn.clicked.connect(self.select_source_file)
        self.save_btn.clicked.connect(self.save_config)

    def _apply_styles(self):
        self.stylesheet_mod = StylesheetModifier(
            "test/configMaker/Styles.qss",
            self
        )
        self.stylesheet_mod.apply_stylesheet()

    # ---------- Core logic ----------

    def select_source_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python Source File",
            str(Path.cwd()),
            "Python Files (*.py)"
        )

        if not file_path:
            return

        self.current_source = Path(file_path)

        class_names = self._extract_class_names(self.current_source)

        if not class_names:
            QMessageBox.critical(
                self,
                "Error",
                "No class definitions found in the selected file."
            )
            return

        if len(class_names) == 1:
            self.entry_point = class_names[0]
        else:
            self.entry_point = self._select_class_popup(class_names)
            if not self.entry_point:
                return

        self.config_text.setPlainText(self._build_ini_preview())
        self.save_btn.setEnabled(True)

    def _extract_class_names(self, file_path: Path) -> list[str]:
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            return [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            ]
        except Exception as e:
            print(e)
            return []

    def _select_class_popup(self, class_names: list[str]) -> str | None:
        selected, ok = QInputDialog.getItem(
            self,
            "Select Entry Point",
            "Multiple classes found.\nSelect entry-point class:",
            class_names,
            0,
            False
        )
        return selected if ok else None

    def _build_ini_preview(self) -> str:
        module_name = self.current_source.stem
        ini_name = f"{module_name}.ini"

        return (
            f"# {ini_name} (must be same name as Python file)\n"
            f"# RendererWidget {self.entry_point}\n\n"
            f"[source]\n"
            f"module = {module_name}\n"
            f"entry_point = {self.entry_point}\n"
            f"description = \n"
        )

    def save_config(self):
        if not self.current_source:
            return

        ini_path = self.current_source.with_suffix(".ini")
        ini_path.write_text(
            self.config_text.toPlainText(),
            encoding="utf-8"
        )

        QMessageBox.information(
            self,
            "Saved",
            f"Config saved:\n{ini_path}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigMaker()
    window.show()
    sys.exit(app.exec())
