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


