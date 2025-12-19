import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenu
)
from PyQt6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu on Menu – Detection Example")
        self.resize(600, 400)

        # Example recent list
        self.recent_paths = [
            "project_a.py",
            "project_b.py",
            "project_c.py",
        ]

        self._build_menu()

    # ---------------- MENU ----------------
    def _build_menu(self):
        menubar = self.menuBar()

        # ---------- FILE (TOP LEVEL) ----------
        self.file_menu = menubar.addMenu("File")

        # 🔹 Detect when TOP menu is opened
        self.file_menu.aboutToShow.connect(self.on_file_menu_opened)

        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: print("Open clicked"))
        self.file_menu.addAction(open_action)

        # ---------- RECENT FILES (SUBMENU) ----------
        self.recent_menu = QMenu("Recent Files", self)
        self.file_menu.addMenu(self.recent_menu)

        # 🔹 Detect when SUBMENU is opened
        self.recent_menu.aboutToShow.connect(self.populate_recent_menu)

        # ---------- EXIT ----------
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.file_menu.addSeparator()
        self.file_menu.addAction(exit_action)

    # ---------------- DETECTION ----------------
    def on_file_menu_opened(self):
        print("📂 File menu opened")

    def populate_recent_menu(self):
        print("🕘 Recent Files menu opened")

        self.recent_menu.clear()

        if not self.recent_paths:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
            return

        for idx, path in enumerate(self.recent_paths[:10], start=1):
            action = QAction(f"{idx}. {path}", self)
            action.setData(path)
            action.triggered.connect(self.on_recent_clicked)
            self.recent_menu.addAction(action)

        self.recent_menu.addSeparator()

        clear_action = QAction("Clear History", self)
        clear_action.triggered.connect(self.clear_recent)
        self.recent_menu.addAction(clear_action)

    # ---------------- ACTION HANDLERS ----------------
    def on_recent_clicked(self):
        action = self.sender()
        if not action:
            return

        path = action.data()
        print(f"📄 Recent clicked: {path}")

    def clear_recent(self):
        print("🧹 Clearing recent files")
        self.recent_paths.clear()


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
