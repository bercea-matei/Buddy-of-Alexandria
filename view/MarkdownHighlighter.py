# MarkdownHighlighter.py

import re
from PyQt6.QtGui import (
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
)
from PyQt6.QtCore import (
    Qt,
)


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.editor = parent
        self.formats = {}
        self.update_formats()

    def update_formats(self):
        """
        Recalculates all text formats based on the editor's current base font.
        This method should be called whenever the base font changes.
        """
        base_font = self.editor.font()
        base_point_size = base_font.pointSize()

        base_format = QTextCharFormat()
        base_format.setFont(base_font)
        self.formats["base"] = base_format

        # --- HEADING FORMATS ---
        self.heading_formats = []
        for i in range(6):
            fmt = QTextCharFormat()
            fmt.setFont(base_font)
            fmt.setFontWeight(QFont.Weight.Bold)
            fmt.setFontPointSize(base_point_size + 16 - int(3.5 * i))
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

        # --- STRIKETHROUGH FORMAT ---
        strikethrough_format = QTextCharFormat()
        strikethrough_format.setFont(base_font)
        strikethrough_format.setFontStrikeOut(True)
        self.formats["strikethrough"] = strikethrough_format

        # --- SYNTAX HIDING FORMAT ---
        self.syntax_format = QTextCharFormat()
        self.syntax_format.setForeground(Qt.GlobalColor.transparent)

        # --- TRIGGER A FULL RE-HIGHLIGHT ---
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

        self.setFormat(0, len(text), self.formats["base"])

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

        # Pattern for ~strikethrough~
        for match in re.finditer(r"(\~)([^\~]+)(\~)", text):
            self.setFormat(match.start(1), 1, self.syntax_format)  # Hide opening *
            self.setFormat(
                match.start(2),
                len(match.group(2)),
                self.formats["strikethrough"],
            )
            self.setFormat(match.start(3), 1, self.syntax_format)  # Hide closing *

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
