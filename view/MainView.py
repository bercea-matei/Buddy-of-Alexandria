# MainView.py

import os

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QTreeView,
    QTabWidget,
)
from PyQt6.QtGui import (
    QFileSystemModel,
)
from PyQt6.QtCore import (
    QDir,
    Qt,
    QStandardPaths,
)
from PyQt6.QtGui import (
    QAction,
    QKeySequence,
)


class MainView(QMainWindow):
    """The main application window."""

    def __init__(self):
        super().__init__()

        # TODO - get_font_from_settings

        documents_location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        app_folder_name = "Academic-Weapon"
        self.root_path = os.path.join(documents_location, app_folder_name)

        self.setWindowTitle("Buddy of Alexandria")
        self.setGeometry(100, 100, 1400, 900)

        self._create_widgets()
        self._create_menu()
        self._load_stylesheet()

    def set_controller(self, controller):
        self.controller = controller

    def _create_widgets(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # File tree view
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Files
        )
        self.file_model.setNameFilters(["*.md"])
        self.file_model.setNameFilterDisables(False)

        os.makedirs(self.root_path, exist_ok=True)
        self.file_model.setRootPath(self.root_path)

        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)

        self.file_tree.setRootIndex(self.file_model.index(self.root_path))

        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(self.root_path))
        # Hide unnecessary columns
        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.hideColumn(3)
        self.file_tree.setMinimumWidth(150)
        splitter.addWidget(self.file_tree)

        # Tab view for editorsa
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        splitter.addWidget(self.tab_widget)

        splitter.setSizes([250, 1150])  # Initial size ratioa

    def _create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        self.open_folder_action = QAction("&Open Folder...", self)
        file_menu.addAction(self.open_folder_action)

        self.new_file_action = QAction("&New File", self)
        self.new_file_action.setShortcut(QKeySequence.StandardKey.New)
        file_menu.addAction(self.new_file_action)

        self.save_file_action = QAction("&Save", self)
        self.save_file_action.setShortcut(QKeySequence.StandardKey.Save)
        file_menu.addAction(self.save_file_action)

        file_menu.addSeparator()
        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)

        tools_menu = menu_bar.addMenu("&Tools")
        self.settings_action = QAction("&Settings...", self)
        tools_menu.addAction(self.settings_action)

    def _load_stylesheet(self):
        style_sheet = "assets/styles.qss"
        try:
            with open(style_sheet, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found. Using default style.")

    def set_file_tree_root(self, path):
        self.file_tree.setRootIndex(self.file_model.index(path))

    def get_current_filepath(self):
        if self.tab_widget.currentIndex() >= 0:
            current_widget = self.tab_widget.currentWidget()
            return current_widget.filepath
        return None

    def get_tab_by_filepath(self, filepath):
        """Helper to find a tab widget instance by its filepath."""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, "filepath") and widget.filepath == filepath:
                return widget
        return None

    def closeEvent(self, event):
        """
        Override the main window's close event.
        Delegate the decision-making to the controller.
        """
        # The controller will decide whether to event.accept() or event.ignore()
        self.controller.handle_exit_request(event)
