# MainView.py

import os

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QTreeView,
    QTabWidget,
    QDockWidget,
    QToolBar,
    QPushButton,
    QSizePolicy,
)
from PyQt6.QtGui import (
    QFileSystemModel,
    QIcon,
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
from view.ChatWidget import ChatWidget

APP_FOLDER_NAME = "BoA"


class MainView(QMainWindow):
    """The main application window."""

    def __init__(self) -> None:
        super().__init__()

        documents_location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )

        self.root_path = os.path.join(documents_location, APP_FOLDER_NAME)

        self.setWindowTitle("Buddy of Alexandria")
        self.setGeometry(100, 100, 1400, 900)

        self._create_docks()
        self._create_menu()
        self._create_toolbar()
        self._create_widgets()
        self._load_stylesheet()

    def set_controller(self, controller) -> None:
        """We need to connect the controller and do some setup"""
        self.controller = controller
        self._after_controller_setup()

    def _after_controller_setup(self) -> None:
        """Run all the methods that require the controller to exist"""
        self.chat_widget.set_controller(self.controller)

    def _create_widgets(self) -> None:
        """Populate Main Window with widgets"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

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

        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.hideColumn(3)
        self.file_tree.setMinimumWidth(150)
        splitter.addWidget(self.file_tree)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)

        # self._setup_new_tab_button()

        size_policy = self.tab_widget.sizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        self.tab_widget.setSizePolicy(size_policy)

        splitter.addWidget(self.tab_widget)

        splitter.setSizes([250, 1150])

    def _setup_new_tab_button(self):
        """TODO/DEPRECATED - DECIDE LATER"""
        button_container = QWidget()

        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 4, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setToolTip("New File")
        self.new_tab_button.setFixedSize(32, 32)
        self.new_tab_button.setObjectName("newFileButton")

        button_layout.addWidget(self.new_tab_button)

        self.tab_widget.setCornerWidget(button_container)

    def _create_docks(self) -> None:
        """Creates all the dockable widgets for the application."""
        self.ai_chat_dock = QDockWidget("BoA chatting session", self)
        self.ai_chat_dock.setObjectName("AIChatDock")

        self.chat_widget = ChatWidget(controller=None)

        self.ai_chat_dock.setWidget(self.chat_widget)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_chat_dock)

    def _create_menu(self) -> None:
        """Menu for settings and preferences"""
        menu_bar = self.menuBar()

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.ai_chat_dock.toggleViewAction())

        tools_menu = menu_bar.addMenu("&Tools")
        self.settings_action = QAction("&Settings...", self)
        tools_menu.addAction(self.settings_action)

        self.open_folder_action = QAction("&Open Folder...", self)
        tools_menu.addAction(self.open_folder_action)

    def _create_toolbar(self) -> None:
        """Toolbar menu for easy access buttons"""
        toolbar = QToolBar("Main ToolBar")
        toolbar.setMovable(False)
        # toolbar.setIconSize(QSize(40, 40))
        self.addToolBar(toolbar)

        self.new_file_action = QAction("&New File", self)
        self.new_file_action.setShortcut(QKeySequence.StandardKey.New)
        toolbar.addAction(self.new_file_action)

        self.save_file_action = QAction(QIcon.fromTheme("document-save"), "&Save", self)
        self.save_file_action.setShortcut(QKeySequence.StandardKey.Save)
        toolbar.addAction(self.save_file_action)

        self.rename_file_action = QAction(
            QIcon.fromTheme("edit-rename"), "&Rename", self
        )
        # self.rename_file_action.setShortcut(QKeySequence.StandardKey.)
        toolbar.addAction(self.rename_file_action)

        self.delete_file_action = QAction(
            QIcon.fromTheme("edit-delete"), "&Delete", self
        )
        # self.delete_file_action.setShortcut(QKeySequence.StandardKey.Delete)
        toolbar.addAction(self.delete_file_action)

        toolbar.addSeparator()

        self.summarize_file_action = QAction("&Summarize", self)
        self.summarize_file_action.setShortcut(QKeySequence.StandardKey.Print)
        toolbar.addAction(self.summarize_file_action)

    def _load_stylesheet(self) -> None:
        """Make it pretty"""
        style_sheet = "assets/styles.qss"
        try:
            with open(style_sheet, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found. Using default style.")

    def set_file_tree_root(self, path) -> None:
        """Set project root"""
        self.file_tree.setRootIndex(self.file_model.index(path))

    def get_current_filepath(self) -> None:
        """Get current filepath"""
        if self.tab_widget.currentIndex() >= 0:
            current_widget = self.tab_widget.currentWidget()
            return current_widget.filepath
        return None

    def get_tab_by_filepath(self, filepath) -> None | QWidget:
        """Helper to find a tab widget instance by its filepath."""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, "filepath") and widget.filepath == filepath:
                return widget
        return None

    def closeEvent(self, event) -> None:
        """
        Override the main window's close event.
        Delegate the decision-making to the controller.
        """
        self.controller.handle_exit_request(event)

    def disable_ai_features(self) -> None:
        self.summarize_file_action.setEnabled(False)
