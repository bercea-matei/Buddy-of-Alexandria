# ChatWidget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtGui import QTextCursor

ASK_BOA_MSG = "How may I help you!"
SEND_BTN_MSG = "-?-"


class ChatWidget(QWidget):
    """
    A self-contained widget for the AI chat interface.
    It has a display area, an input box, and a send button.
    """

    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller
        if controller is not None:
            self.set_controller(controller=self.controller)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask the BoA something...")

        self.send_button = QPushButton(SEND_BTN_MSG)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.chat_display)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.send_button)

    def set_controller(self, controller) -> None:
        """
        Sets the reference to the controller and loads necessary functions.
        Use this if you pass None to the controller initially
        """
        self.controller = controller
        self.send_button.clicked.connect(self.controller.handle_send_chat_message)
        self.input_box.returnPressed.connect(self.controller.handle_send_chat_message)

    def add_message(self, sender, text) -> None:
        """Appends a message to the chat display, formatted with HTML for style."""
        if sender.lower() == "user":
            color = "#569cd6"
            font_weight = "bold"
        else:
            color = "#ce9178"
            font_weight = "bold"

        formatted_message = (
            f'<hr><p style="color:{color}; font-weight:{font_weight};'
            + f'">{sender}:</p><p>{text}</p><hr style="background-color: transparent; height: 1px; border: 0;"> '
        )
        self.chat_display.append(formatted_message)

    def get_input_text(self) -> str:
        """Returns the text from the input box and clears it."""
        text = self.input_box.text()
        self.input_box.clear()
        return text

    def append_to_last_message(self, text_chunk: str) -> None:
        """Appends text to the last message"""
        count = self.layout.count()
        if count == 0:
            return

        # -1 => the send button
        # -2 => the input box
        # -3 => QTextEdit
        last_item = self.layout.itemAt(count - 3)
        last_widget = last_item.widget()

        if last_widget:
            cursor = last_widget.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(text_chunk)
            last_widget.ensureCursorVisible()

    def set_disabled_state(self, reason_msg: str = "idk") -> None:
        self.send_button.setEnabled(False)
        self.input_box.setEnabled(False)
        self.add_message("System", reason_msg)
