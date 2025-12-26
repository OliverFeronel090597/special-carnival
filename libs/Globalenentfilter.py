from PyQt6.QtCore import QObject, QEvent


# -----------------------------
# Global Event Filter
# -----------------------------
class GlobalEventFilter(QObject):
    def eventFilter(self, obj: QObject, event: QEvent):

        # Detect mouse clicks
        if event.type() == QEvent.Type.MouseButtonPress:
            print(
                f"[MOUSE PRESS] "
                f"Widget={obj.__class__.__name__} "
                f"objectName='{obj.objectName()}'"
            )

        # Detect key presses
        elif event.type() == QEvent.Type.KeyPress:
            print(
                f"[KEY PRESS] "
                f"Widget={obj.__class__.__name__} "
                f"Key={event.key()}"
            )

        # Detect focus changes
        elif event.type() == QEvent.Type.FocusIn:
            print(
                f"[FOCUS IN] "
                f"Widget={obj.__class__.__name__} "
                f"objectName='{obj.objectName()}'"
            )

        # IMPORTANT:
        # Return False to allow normal processing to continue
        return False


# # -----------------------------
# # Main UI
# # -----------------------------
# class DemoWindow(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Qt6 Event Filter Demo")
#         self.resize(400, 300)

#         layout = QVBoxLayout(self)

#         label = QLabel("Click buttons or type in the editor")
#         label.setObjectName("InfoLabel")

#         btn1 = QPushButton("Button One")
#         btn1.setObjectName("BtnOne")

#         btn2 = QPushButton("Button Two")
#         btn2.setObjectName("BtnTwo")

#         editor = QTextEdit()
#         editor.setObjectName("Editor")

#         layout.addWidget(label)
#         layout.addWidget(btn1)
#         layout.addWidget(btn2)
#         layout.addWidget(editor)


# # -----------------------------
# # Application entry point
# # -----------------------------
# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     # Install GLOBAL event filter
#     event_filter = GlobalEventFilter()
#     app.installEventFilter(event_filter)

#     window = DemoWindow()
#     window.show()

#     sys.exit(app.exec())
