# LiveMarkdownEditor.py

from PyQt6.QtWidgets import (
    QTextEdit,
)
from PyQt6.QtGui import (
    QTextListFormat,
    QTextCursor,
)
from PyQt6.QtGui import (
    QColor,
    QTextBlockFormat,
)
from view.MarkdownHighlighter import MarkdownHighlighter


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

        self.previous_cursor_block = -1
        self.cursorPositionChanged.connect(self._on_cursor_move)

    def format_block_as_list(self, block_number):
        """This method is called directly by the highlighter to create a list item."""
        block = self.document().findBlockByNumber(block_number)
        if not block.isValid():
            return

        cursor = QTextCursor(block)

        if not cursor.currentList():
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.Style.ListDisc)
            cursor.beginEditBlock()
            cursor.createList(list_format)
            cursor.endEditBlock()

    def _on_cursor_move(self):
        """When cursor moves, re-highlight old/new lines to toggle rendering."""
        current_block_num = self.textCursor().blockNumber()
        if self.previous_cursor_block != current_block_num:
            if self.previous_cursor_block >= 0:
                block = self.document().findBlockByNumber(self.previous_cursor_block)
                if block.isValid():
                    self.highlighter.rehighlightBlock(block)

            self.highlighter.rehighlightBlock(self.textCursor().block())

            cursor = self.textCursor()
            if cursor.currentList():
                cursor.createList(QTextListFormat())

            self.previous_cursor_block = current_block_num

    def set_content(self, text):
        """Sets the editor's content and ensures all formatting
        is applied on load."""
        self.setPlainText(text)
        self.highlighter.rehighlight()

    def get_content(self):
        return self.toPlainText()

    def update_highlighter_formats(self):
        if hasattr(self, "highlighter"):
            self.highlighter.update_formats()
