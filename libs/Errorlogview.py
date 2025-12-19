from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class ErrorLogView(QTextEdit):
    """
    Read-only rich-text log view for validator / analysis output.
    Designed for HTML-formatted messages.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setReadOnly(True)
        self.setAcceptRichText(True)
        self.setUndoRedoEnabled(False)
        # self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        font = QFont("Consolas")
        font.setPointSize(10)
        self.setFont(font)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.clear_with_placeholder()

    # ---------- API ----------
    def log_html(self, html: str):
        """Append HTML-formatted message."""
        self.clear()
        self.moveCursor(self.textCursor().MoveOperation.End)
        self.insertHtml(html + "<br>")
        self.moveCursor(self.textCursor().MoveOperation.End)

    def log_ok(self, message: str):
        self.clear()
        self.log_html(
            f"<span style='color:#68d391;'>✔ {message}</span>"
        )

    def log_warning(self, message: str):
        self.clear()
        self.log_html(
            f"<span style='color:#f6ad55;'>⚠ {message}</span>"
        )

    def log_error(self, message: str):
        self.clear()
        self.log_html(
            f"<span style='color:#f56565;'>✖ {message}</span>"
        )

    def clear_with_placeholder(self):
        self.clear()
        # self.setPlaceholderText("No validation messages")
        # self.setHtml(
        #     "<span style='color:#718096;'>"
        #     "No validation messages\n."
        #     "</span>"
        # )
