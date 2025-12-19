from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout
)
from PyQt6.QtGui import (
    QPainter, QColor
)
from PyQt6.QtCore import (
        Qt
)

class SafeWidgetWrapper(QWidget):
    """Wraps a widget to catch paint and event errors."""
    
    def __init__(self, widget: QWidget):
        super().__init__()
        self.wrapped_widget = widget
        self.has_error = False
        self.error_message = ""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        
    def paintEvent(self, event):
        """Override to catch paint errors."""
        try:
            super().paintEvent(event)
        except Exception as e:
            self.has_error = True
            self.error_message = str(e)
            
            # Draw error overlay
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(255, 240, 240, 200))
            painter.setPen(Qt.GlobalColor.red)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                           f"Paint Error: {str(e)[:50]}...")
            
    def event(self, event):
        """Catch all events to prevent crashes."""
        try:
            return super().event(event)
        except Exception as e:
            self.has_error = True
            self.error_message = str(e)
            print(f"Event error caught: {e}")
            return True  # Event handled