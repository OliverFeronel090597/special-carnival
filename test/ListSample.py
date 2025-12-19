import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget,
    QVBoxLayout, QListWidget
)


class ListDoubleClickApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Double Click Print")

        self.list_widget = QListWidget()
        self.list_widget.addItems([
            "Item A",
            "Item B",
            "Item C",
            "Item D"
        ])

        # signal emitted on double click
        self.list_widget.itemDoubleClicked.connect(self.print_item)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)

    def print_item(self, item):
        print(item.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ListDoubleClickApp()
    w.resize(300, 200)
    w.show()
    sys.exit(app.exec())
