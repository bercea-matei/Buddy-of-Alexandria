# view.py

import os

import markdown
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTreeView,
    QTabWidget,
    QPlainTextEdit,
    QDialog,
    QFormLayout,
    QFontComboBox,
    QSpinBox,
    QDialogButtonBox,
    QScrollArea,
    QTextEdit,
)
from PyQt6.QtGui import (
    QFileSystemModel,  # <-- ADD THIS
    QTextListFormat,  # <-- ADD THIS
    QTextCursor,  # <-- ADD THIS
)
from PyQt6.QtCore import (
    QDir,
    Qt,
    QStandardPaths,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import (
    QAction,
    QFont,
    QKeySequence,
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QTextBlockFormat,
)
import re


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.editor = parent  # The parent is the QTextEdit document
        self.formats = {}
        self.update_formats()

    def update_formats(self):
        """
        Recalculates all text formats based on the editor's current base font.
        This method should be called whenever the base font changes.
        """
        base_font = self.editor.font()
        base_point_size = base_font.pointSize()

        # --- HEADING FORMATS ---
        self.heading_formats = []
        for i in range(6):
            fmt = QTextCharFormat()
            fmt.setFont(base_font)  # Start with the base font
            # fmt.setForeground(QColor("#569cd6"))
            fmt.setFontWeight(QFont.Weight.Bold)
            fmt.setFontPointSize(base_point_size + 16 - 3 * i)
            self.heading_formats.append(fmt)

        # --- BOLD FORMAT ---
        bold_format = QTextCharFormat()
        bold_format.setFont(base_font)
        bold_format.setFontWeight(QFont.Weight.Bold)
        self.formats["bold"] = bold_format

        # --- ITALIC FORMAT ---
        italic_format = QTextCharFormat()
        italic_format.setFont(base_font)
        italic_format.setFontItalic(True)
        self.formats["italic"] = italic_format

        # --- SYNTAX HIDING FORMAT ---
        self.syntax_format = QTextCharFormat()
        self.syntax_format.setForeground(Qt.GlobalColor.transparent)

        # --- TRIGGER A FULL RE-HIGHLIGHT ---
        # This is crucial. It tells the editor to apply our new formats everywhere.
        self.rehighlight()

    def highlightBlock(self, text):
        current_block = self.currentBlock()
        block_number = current_block.blockNumber()
        is_current_line = (
            current_block.blockNumber() == self.editor.textCursor().blockNumber()
        )
        if text.startswith("> "):
            self.editor.format_block_as_blockquote(block_number)
        elif re.match(r"^\s*([\*\-\+])\s", text):
            # For list items, we only want the structural change to happen on non-active lines
            if not is_current_line:
                self.editor.format_block_as_list(block_number)
        # else:
        # It's a plain block of text
        # self.editor.format_block_as_plain(block_number)

        # Now, handle character formatting and syntax hiding
        if is_current_line:
            self.setFormat(0, len(text), self.editor.currentCharFormat())
            if text.startswith("> "):  # Still hide syntax on current line
                self.setFormat(0, 2, self.syntax_format)
            return

        if is_current_line:
            self.setFormat(0, len(text), self.editor.currentCharFormat())
            return

        # Pattern for *italic*
        for match in re.finditer(r"(\*)([^\*]+)(\*)", text):
            # Check if this is part of an already-processed bold
            if self.format(match.start(1)).fontWeight() != QFont.Weight.Bold:
                self.setFormat(match.start(1), 1, self.syntax_format)  # Hide opening *
                self.setFormat(
                    match.start(2), len(match.group(2)), self.formats["italic"]
                )
                self.setFormat(match.start(3), 1, self.syntax_format)  # Hide closing *

        # Pattern for **bold**
        for match in re.finditer(r"(\*\*)([^\*]+)(\*\*)", text):
            self.setFormat(match.start(1), 2, self.syntax_format)  # Hide opening **
            self.setFormat(match.start(2), len(match.group(2)), self.formats["bold"])
            self.setFormat(match.start(3), 2, self.syntax_format)  # Hide closing **

        # --- HEADINGS (up to 6 levels) ---
        match = re.match(r"^(#{1,6})\s(.+)", text)
        if match:
            heading_level = len(match.group(1))
            self.setFormat(
                match.start(1), heading_level + 1, self.syntax_format
            )  # Hide the # and space
            self.setFormat(
                match.start(2),
                len(match.group(2)),
                self.heading_formats[heading_level - 1],
            )

        # --- BULLET POINTS ---
        match = re.match(r"^\s*([\*\-\+])\s", text)
        if match:
            # Only hide the syntax. The editor handles the structure.
            self.setFormat(match.start(1), len(match.group(1)) + 1, self.syntax_format)


class LiveMarkdownEditor(QTextEdit):
    """
    A QTextEdit that uses direct calls from its highlighter to create lists
    and handles reverting to raw text for editing.
    """

    def __init__(self, filepath, font):
        super().__init__()
        self.filepath = filepath

        self.setFont(font)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0; border: none;")

        self.highlighter = MarkdownHighlighter(self)

        self.default_block_format = QTextBlockFormat()
        self.blockquote_format = QTextBlockFormat()
        self.blockquote_format.setLeftMargin(20)
        self.blockquote_format.setBackground(QColor("#3a3d41"))

        # NOTE: We no longer need the textChanged connection for block formatting.
        # It will be handled by the highlighter and cursor movement.

        self.previous_cursor_block = -1
        self.cursorPositionChanged.connect(self._on_cursor_move)

    def format_block_as_list(self, block_number):
        """This method is called directly by the highlighter to create a list item."""
        block = self.document().findBlockByNumber(block_number)
        if not block.isValid():
            return

        cursor = QTextCursor(block)

        # Only create a list if the block is not already part of one
        if not cursor.currentList():
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.Style.ListDisc)
            # Grouping in an edit block makes this a single undo step
            cursor.beginEditBlock()
            cursor.createList(list_format)
            cursor.endEditBlock()

    def _on_cursor_move(self):
        """When cursor moves, re-highlight old/new lines to toggle rendering."""
        current_block_num = self.textCursor().blockNumber()
        if self.previous_cursor_block != current_block_num:
            # Re-highlight the line we just left. This will trigger format_block_as_list
            # if it's a list item, turning it into a rendered bullet.
            if self.previous_cursor_block >= 0:
                block = self.document().findBlockByNumber(self.previous_cursor_block)
                if block.isValid():
                    self.highlighter.rehighlightBlock(block)

            # Re-highlight the line we just entered. This will show it as raw text.
            self.highlighter.rehighlightBlock(self.textCursor().block())

            # THE CRUCIAL PART: If the line we moved TO is a list item,
            # we must temporarily remove the list formatting so the user can
            # see and edit the raw "* " text.
            cursor = self.textCursor()
            if cursor.currentList():
                # Passing an empty QTextListFormat to createList removes the item from the list.
                cursor.createList(QTextListFormat())

            self.previous_cursor_block = current_block_num

    def set_content(self, text):
        """Sets the editor's content and ensures all formatting is applied on load."""
        self.setPlainText(text)
        # A single rehighlight will cause the highlighter to run on all blocks
        # and call format_block_as_list for every bullet point it finds.
        self.highlighter.rehighlight()

    def get_content(self):
        return self.toPlainText()

    def update_highlighter_formats(self):
        if hasattr(self, "highlighter"):
            self.highlighter.update_formats()


class EditorTab(QWidget):
    """A widget containing a splitter with a text editor and a markdown preview."""

    def __init__(self, filepath, content, font):
        super().__init__()
        self.filepath = filepath

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self.editor = QPlainTextEdit()
        self.editor.setPlainText(content)
        self.editor.setFont(font)
        splitter.addWidget(self.editor)

        self.preview = QWebEngineView()
        splitter.addWidget(self.preview)

        self.update_preview()

        # Connect text changed signal to update preview
        self.editor.textChanged.connect(self.update_preview)

    def update_preview(self):
        text = self.editor.toPlainText()
        html = markdown.markdown(text, extensions=["fenced_code", "tables"])
        self.preview.setHtml(html)


class SettingsDialog(QDialog):
    """A scrollable settings dialog."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)

        form_layout = QFormLayout(container)

        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setCurrentFont(QFont(settings.get("font_family")))
        form_layout.addRow("Font Family:", self.font_family_combo)

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(72)
        self.font_size_spinbox.setValue(settings.get("font_size", 12))
        form_layout.addRow("Font Size:", self.font_size_spinbox)

        # Add more settings here in the future

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_settings(self):
        return {
            "font_family": self.font_family_combo.currentFont().family(),
            "font_size": self.font_size_spinbox.value(),
        }


class MainView(QMainWindow):
    """The main application window."""

    def __init__(self):
        super().__init__()

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

        # Tab view for editors
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        splitter.addWidget(self.tab_widget)

        splitter.setSizes([250, 1150])  # Initial size ratio

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
        try:
            with open("styles.qss", "r") as f:
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
