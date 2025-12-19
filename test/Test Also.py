import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtCharts import QChart, QChartView, QLineSeries
from PyQt6.QtGui import QPainter


# =======================
# CONFIG: swap host here
# =======================
USE_MAINWINDOW = True   # False -> QWidget


# =======================
# Renderer (shared logic)
# =======================
class RendererWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.status_label = QLabel("Renderer idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size:14px; font-weight:bold;")

        # --- chart ---
        self.series = QLineSeries()
        self.series.append(0, 0)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.setTitle("Live Data (Renderer Test)")

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- controls ---
        self.btn_update = QPushButton("Update Renderer")
        self.btn_update.clicked.connect(self.update_renderer)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Mode A", "Mode B", "Mode C"])

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.btn_update)
        control_layout.addWidget(self.combo_mode)

        # --- layout ---
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addLayout(control_layout)
        layout.addWidget(self.chart_view)

        self.x = 0

    # Assuming you have a renderer widget
    def update_renderer(self, module):
        """
        Update renderer widget only if module loaded correctly
        and has the required class (Painter).
        """
        if not module:
            print("Module load failed. Skipping renderer update.")
            return

        try:
            # Ensure Painter exists
            if hasattr(module, "Painter"):
                # Remove old widget(s)
                for child in self.renderer.findChildren(QWidget):
                    child.deleteLater()
                
                painter_widget = module.Painter(self.renderer)
                self.renderer.layout().addWidget(painter_widget)
            else:
                print("Module loaded but Painter class not found. Skipping update.")
        except Exception as e:
            print(f"Error updating renderer: {e}")


# =======================
# Host: QMainWindow
# =======================
class MainWindowHost(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Renderer Test – QMainWindow")

        self.renderer = RendererWidget()
        self.setCentralWidget(self.renderer)

        self._auto_update()


    def _auto_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.renderer.update_renderer)
        self.timer.start(1500)


# =======================
# Host: QWidget
# =======================
class WidgetHost(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Renderer Test – QWidget")

        self.renderer = RendererWidget()

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        frame_layout.addWidget(self.renderer)

        layout = QVBoxLayout(self)
        layout.addWidget(frame)

        self._auto_update()

    def _auto_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.renderer.update_renderer)
        self.timer.start(1500)


# =======================
# Entry point
# =======================
# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     Host = MainWindowHost if USE_MAINWINDOW else WidgetHost
#     win = Host()
#     win.resize(800, 500)
#     win.show()

#     sys.exit(app.exec())
