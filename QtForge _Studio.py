"""
Dynamic Source Loader and Renderer Host
A professional Qt application for embedding external Python-Qt modules at runtime.
Complete with auto-reload functionality and detachable renderer.
"""

import sys
import os
from pathlib                    import Path
from typing                     import Optional, Any

from PyQt6.QtCore               import (Qt, QTimer, QSettings, 
                                        QFileSystemWatcher, QDateTime, pyqtSlot)
from PyQt6.QtWidgets            import (
                                QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QLabel, QFrame, QFileDialog, QMenu,
                                QCheckBox, QGroupBox, QProgressBar)
from PyQt6.QtGui                import (QFont, QIcon, QAction)

from libs.Detachablerenderer    import DetachableRenderer
from libs.Sourcevalidator       import SourceValidator
from libs.Safewidgetwrapper     import SafeWidgetWrapper
from libs.stylesheetModefier    import StylesheetModifier
from libs.Errorlogview          import ErrorLogView
from libs.Databasconnector      import DatabaseConnector

# ----------------- Main Application -----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_source: Optional[Path] = None
        self.current_module: Optional[Any] = None
        self.validator_thread: Optional[SourceValidator] = None
        self.hosted_widget: Optional[QWidget] = None
        self.raw_widget: Optional[QWidget] = None

        self.styleSheet_mod = StylesheetModifier("src/styles.qss", self)
        self.styleSheet_mod.apply_stylesheet()

        self.file_watcher = QFileSystemWatcher()
        self.last_modification: dict[str, float] = {}
        self.reload_timer = QTimer()
        self.reload_timer.setSingleShot(True)
        self.reload_timer.setInterval(1500)
        self.reload_timer.timeout.connect(self.debounced_reload)

        self.is_reloading = False
        self.recent_files: list[Path] = []

        self.db = DatabaseConnector()
        self.db.create_tables_if_not_exist()

        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        self.apply_main_stylesheet()

    # ----------------- Window / UI -----------------
    def setup_window(self):
        self.setWindowIcon(QIcon("img/QtForge Studio.png"))
        self.setWindowTitle("Dynamic Source Loader Host")
        self.setGeometry(100, 100, 1400, 900)
        self.settings = QSettings("DynamicLoader", "HostApp")
        if self.settings.contains("window/geometry"):
            self.restoreGeometry(self.settings.value("window/geometry"))
        if self.settings.contains("window/state"):
            self.restoreState(self.settings.value("window/state"))

    def apply_main_stylesheet(self):
        self.styleSheet_mod.apply_stylesheet()

    def setup_ui(self):
        self.btn_select = QPushButton("📂 Open")
        self.btn_reload = QPushButton("🔄 Reload")
        self.btn_reload.setEnabled(False)

        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self.renderer = DetachableRenderer(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.renderer)

        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        main_layout.addStretch()

        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        # --- Open ---
        open_action = QAction("&Open Source Folder", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.select_source_folder)
        file_menu.addAction(open_action)

        # --- Recent files submenu ---
        self.recent_menu = QMenu("&Open Recent", self)
        file_menu.addMenu(self.recent_menu)
        self.recent_paths = []  # list of Path objects or str

        # Populate recent dynamically when menu opens
        self.recent_menu.aboutToShow.connect(self.populate_recent_menu)

        # --- Reload ---
        reload_action = QAction("&Reload Source", self)
        reload_action.setShortcut("F5")
        reload_action.triggered.connect(self.reload_source)
        file_menu.addAction(reload_action)

        file_menu.addSeparator()

        # --- Exit ---
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ----------------- View Menu -----------------
        view_menu = menubar.addMenu("&View")
        toggle_renderer_action = QAction("&Toggle Renderer", self)
        toggle_renderer_action.setShortcut("Ctrl+R")
        toggle_renderer_action.triggered.connect(self.toggle_renderer)
        detach_renderer_action = QAction("&Detach/Attach Renderer", self)
        detach_renderer_action.setShortcut("Ctrl+D")
        detach_renderer_action.triggered.connect(self.toggle_detach_renderer)
        reset_layout_action = QAction("&Reset Layout", self)
        reset_layout_action.triggered.connect(self.reset_layout)
        view_menu.addActions([toggle_renderer_action, detach_renderer_action, reset_layout_action])

        # ----------------- Settings Menu -----------------
        settings_menu = menubar.addMenu("&Settings")
        theme_action = QAction("&Toggle Theme", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(theme_action)


    # ----------------- Populate Recent Menu -----------------
    def populate_recent_menu(self):
        self.recent_menu.clear()
        self.recent_paths = self.db.get_recent_paths(10)
        if not self.recent_paths:
            empty_action = QAction("No Recent Files", self)
            empty_action.setEnabled(False)
            self.recent_menu.addAction(empty_action)
            return



        # Only keep latest 10
        for idx, path in enumerate(self.recent_paths[:10], start=1):
            action = QAction(f"{idx}. {path.name if hasattr(path, 'name') else path}", self)
            action.setData(path)
            action.triggered.connect(self.on_recent_file_selected)
            self.recent_menu.addAction(action)

        self.recent_menu.addSeparator()
        # clear_action = QAction("Clear History", self)
        # clear_action.triggered.connect(self.clear_recent_files)
        # self.recent_menu.addAction(clear_action)

    # ----------------- Handlers -----------------
    def on_recent_file_selected(self):
        action :QAction= self.sender()
        path_str = action.data()  # we stored the path in action.setData()
        folder_path = Path(path_str)  # <-- convert to Path
        self.load_source(folder_path)

    # def clear_recent_files(self): # no need to remove paths
    #     self.recent_paths.clear()

    def create_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.addWidget(self.btn_select)
        toolbar.addWidget(self.btn_reload)
        detach_btn = QPushButton("⤢ Detach")
        detach_btn.clicked.connect(self.toggle_detach_renderer)
        toolbar.addWidget(detach_btn)
        toolbar.addSeparator()
        self.auto_reload_indicator = QLabel("⏰ OFF")
        toolbar.addWidget(self.auto_reload_indicator)

    def create_status_bar(self):
        status_bar = self.statusBar()
        self.ready_label = QLabel("Ready")
        status_bar.addWidget(self.ready_label)
        self.watcher_status_label = QLabel("🔒 No files watched")
        status_bar.addWidget(self.watcher_status_label)
        self.memory_label = QLabel("")
        status_bar.addPermanentWidget(self.memory_label)
        timer = QTimer()
        timer.timeout.connect(self.update_memory_usage)
        timer.start(5000)
        self.update_memory_usage()

    def update_memory_usage(self):
        try:
            import psutil
            mem = psutil.Process().memory_info().rss / 1024 / 1024
            self.memory_label.setText(f"🧠 {mem:.1f} MB")
        except ImportError:
            self.memory_label.setText("🧠 N/A")

    def create_control_panel(self) -> QFrame:
        control_panel = QFrame()
        layout = QVBoxLayout(control_panel)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Dynamic Source Loader")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont(); f.setPointSize(16); f.setBold(True)
        title.setFont(f)
        title.setStyleSheet("color: #ffffff; padding: 10px;")
        layout.addWidget(title)

        desc = QLabel("Load and host external Python-Qt applications dynamically")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #cbd5e0; padding-bottom: 15px;")
        layout.addWidget(desc)

        btn_layout = QHBoxLayout()
        self.btn_select.setFixedHeight(36)
        self.btn_reload.setFixedHeight(36)
        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(self.btn_reload)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        status_layout = QHBoxLayout()
        self.lbl_status = QLabel("No source loaded")
        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch()
        self.auto_reload_check = QCheckBox("⏰ Auto-reload on file change")
        status_layout.addWidget(self.auto_reload_check)
        layout.addLayout(status_layout)

        source_group = QGroupBox("📄 Source Information")
        g_layout = QVBoxLayout()
        self.source_info_label = QLabel("No source selected")
        self.source_info_label.setWordWrap(True)
        self.watched_files_label = QLabel("Watching 0 files")
        g_layout.addWidget(self.source_info_label)
        g_layout.addWidget(self.watched_files_label)
        source_group.setLayout(g_layout)
        layout.addWidget(source_group)

        self.error_view = ErrorLogView()
        self.error_view.setReadOnly(True)
        self.error_view.setAcceptRichText(True)

        layout.addWidget(self.error_view)


        return control_panel

    # ----------------- Connections -----------------
    def setup_connections(self):
        self.btn_select.clicked.connect(self.select_source_folder)
        self.btn_reload.clicked.connect(self.reload_source)
        self.auto_reload_check.stateChanged.connect(self.on_auto_reload_changed)

    # ----------------- File / Source Loading -----------------
    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder", str(Path.home()))
        if folder:
            self.load_source(Path(folder))

    def load_source(self, folder_path: Path):
        print(folder_path)
        ini_files = list(folder_path.glob("*.ini"))
        if not ini_files:
            self.error_view.log_error(f"No Config Files No .ini config files found in {folder_path}")
            return
        self.db.insert_path(folder_path, self.get_curr_date_time())

        config_file = ini_files[0]
        import configparser
        config = configparser.ConfigParser()
        config.read(config_file)
        module_name = config.get('source', 'module', fallback=None)
        if not module_name:
            self.error_view.log_error(f"Invalid Config module specified in {config_file.name}")
            return

        module_path = folder_path / f"{module_name}.py"
        if not module_path.exists():
            self.error_view.log_error(f"Module Not Found {module_name}.py not found in {folder_path}")
            return

        self.current_source = module_path
        self.source_info_label.setText(f"📄 Source: {module_path.name}\n⚙️ Config: {config_file.name}\n📁 Path: {module_path.parent}")

        # Add to recent files
        if module_path in self.recent_files:
            self.recent_files.remove(module_path)
        self.recent_files.insert(0, module_path)
        if len(self.recent_files) > 10:
            self.recent_files.pop()

        self.start_validation(module_path)

    # ----------------- Validation / Widget -----------------
    def start_validation(self, source_path: Path):
        if self.validator_thread and self.validator_thread.isRunning():
            self.validator_thread.stop()
            self.validator_thread.wait()

        self.btn_select.setEnabled(False)
        self.btn_reload.setEnabled(False)
        self.lbl_status.setText("Validating source...")
        self.progress_bar.setValue(0)

        self.validator_thread = SourceValidator(source_path)
        self.validator_thread.preflight_check.connect(self.on_preflight_check)
        self.validator_thread.validation_complete.connect(self.on_validation_complete)
        self.validator_thread.progress_update.connect(self.on_progress_update)
        self.validator_thread.finished.connect(self.on_validation_finished)
        self.validator_thread.start()

    @pyqtSlot(int, str)
    def on_progress_update(self, progress: int, message: str):
        self.progress_bar.setValue(progress)
        self.lbl_status.setText(message if progress < 100 else self.lbl_status.text())

    @pyqtSlot(bool, str)
    def on_preflight_check(self, success: bool, message: str):
        color = "#48bb78" if success else "#f56565"
        self.lbl_status.setText(f"<span style='color:{color}'>{message}</span>")

    @pyqtSlot(bool, str, object)
    def on_validation_complete(self, success: bool, message: str, module: Any):
        if success and module:
            self.current_module = module
            self.instantiate_widget(module)
            self.lbl_status.setText(f"<span style='color:#48bb78'>{message}</span>")
            self.btn_reload.setEnabled(True)
            if self.auto_reload_check.isChecked():
                QTimer.singleShot(1000, self.enable_file_watching)
        else:
            self.error_view.log_error(f"Load Failed {message}")
            self.lbl_status.setText("<span style='color:#f56565'>Load failed</span>")

    @pyqtSlot()
    def on_validation_finished(self):
        self.btn_select.setEnabled(True)
        self.progress_bar.hide()
        self.ready_label.setText("Ready")

    def instantiate_widget(self, module: Any):
        """
        Safely instantiate the entry point widget from the module.
        Prevent crashes if the module has typos or missing classes.
        """
        if not module:
            self.error_view.log_error("Load Failed Module is None")
            return

        try:
            import configparser
            config_path = self.current_source.parent / f"{self.current_source.stem}.ini"
            config = configparser.ConfigParser()
            config.read(config_path)
            entry_point = config.get('source', 'entry_point', fallback='main_widget')
            widget_factory = getattr(module, entry_point, None)

            if not widget_factory:
                raise AttributeError(f"Entry point '{entry_point}' not found in module")

            try:
                widget = widget_factory()
            except Exception as e:
                raise RuntimeError(f"Failed to create widget from '{entry_point}': {e}")

            if not isinstance(widget, QWidget):
                raise TypeError(f"Entry point must return QWidget, got {type(widget)}")

            # Wrap in safe widget wrapper
            safe_widget = SafeWidgetWrapper(widget)
            self.renderer.host_widget(safe_widget)
            self.hosted_widget = safe_widget
            self.raw_widget = widget
            self.ready_label.setText(f"✅ Hosting: {widget.__class__.__name__}")

        except Exception as e:
            self.error_view.log_error(f"Widget Instantiation Failed {str(e)}")
            self.lbl_status.setText("<span style='color:#f56565'>Widget creation failed</span>")
            self.renderer.clear()

    # ----------------- Auto-reload -----------------
    def on_auto_reload_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            self.enable_file_watching()
            self.auto_reload_indicator.setText("⏰ ON")
        else:
            self.disable_file_watching()
            self.auto_reload_indicator.setText("⏰ OFF")

    def enable_file_watching(self):
        if not self.current_source or self.is_reloading:
            return

        self.file_watcher.blockSignals(True)

        # Iterate over desired file extensions
        paths = []
        for ext in ("*.py", "*.ini", "*.qss"):
            paths.extend(str(p) for p in self.current_source.parent.rglob(ext))

        self.file_watcher.removePaths(self.file_watcher.files())
        self.file_watcher.addPaths(paths)
        self.file_watcher.blockSignals(False)

        self.file_watcher.fileChanged.connect(self.on_file_changed)
        self.watcher_status_label.setText(f"👁️ Watching {len(paths)} files")
        self.watched_files_label.setText(f"Watching {len(paths)} file(s) for changes")

    def disable_file_watching(self):
        try:
            self.file_watcher.fileChanged.disconnect()
        except Exception:
            pass
        self.file_watcher.removePaths(self.file_watcher.files())
        self.watcher_status_label.setText("🔒 No files watched")
        self.watched_files_label.setText("Watching 0 files")

    def on_file_changed(self, path: str):
        if self.is_reloading or not self.auto_reload_check.isChecked():
            return
        if not os.path.exists(path):
            QTimer.singleShot(1000, lambda: self.reenable_file_watching(path))
            return
        mtime = os.path.getmtime(path)
        last = self.last_modification.get(path, 0)
        if mtime > last + 0.1:
            self.last_modification[path] = mtime
            self.lbl_status.setText(f"<span style='color:#ed8936'>🔄 {os.path.basename(path)} changed</span>")
            self.reload_timer.start()

    def reenable_file_watching(self, path):
        if os.path.exists(path) and self.auto_reload_check.isChecked():
            try:
                self.file_watcher.addPath(path)
                self.last_modification[path] = os.path.getmtime(path)
            except Exception:
                pass

    def debounced_reload(self):
        if self.current_source and not self.is_reloading:
            self.is_reloading = True
            self.lbl_status.setText("<span style='color:#4299e1'>🔄 Auto-reloading source...</span>")
            QTimer.singleShot(500, self.perform_auto_reload)

    def perform_auto_reload(self):
        try:
            self.renderer.begin_update()
            self.renderer.clear()
            if self.current_source:
                mod_name = self.current_source.stem
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
            self.start_validation(self.current_source)
            self.renderer.end_update()
        finally:
            self.is_reloading = False

    def reload_source(self):
        if self.current_source:
            self.start_validation(self.current_source)

    # ----------------- Utilities -----------------
    def toggle_renderer(self):
        self.renderer.setVisible(not self.renderer.isVisible())

    def toggle_detach_renderer(self):
        self.renderer.toggle_detached()

    def reset_layout(self):
        self.renderer.setVisible(True)
        self.renderer.resetDockWidget()
        self.showNormal()

    def toggle_theme(self):
        self.styleSheet_mod.toggle_theme()

    def get_curr_date_time(self) -> str:
        now = QDateTime.currentDateTime()
        return now.toString("yyyy-MM-dd HH:mm:ss")

    def closeEvent(self, event):
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/state", self.saveState())
        self.disable_file_watching()
        if self.validator_thread and self.validator_thread.isRunning():
            self.validator_thread.stop()
            self.validator_thread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
