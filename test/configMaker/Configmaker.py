from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
import sys
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.select_file = QPushButton("XXX")
        self.select_file.setFixedSize(50, 30)
        main_layout.addWidget(self.select_file)       
        
        self.select_file.clicked.connect(self.select_source_file)

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
        print(self.current_source)          # file
        print(self.current_source.parent)   # directory



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())