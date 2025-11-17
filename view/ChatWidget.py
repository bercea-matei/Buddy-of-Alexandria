from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton

ASK_BOA_MSG = "How may I help you!"
SEND_BTN_MSG = "-?-"


class ChatWidget(QWidget):
    """
    A self-contained widget for the AI chat interface.
    It has a display area, an input box, and a send button.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask the BoA something...")

        self.send_button = QPushButton(SEND_BTN_MSG)

        layout = QVBoxLayout(self)
        layout.addWidget(self.chat_display)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)

    def set_controller(self, controller):
        self.controller = controller
        self.send_button.clicked.connect(self.controller.handle_send_chat_message)
        self.input_box.returnPressed.connect(self.controller.handle_send_chat_message)

    def add_message(self, sender, text):
        """Appends a message to the chat display, formatted with HTML for style."""
        if sender.lower() == "user":
            color = "#569cd6"
            font_weight = "bold"
        else:
            color = "#ce9178"
            font_weight = "normal"

        formatted_message = f'<p style="color:{color}; font-weight:{font_weight};">{sender}:</p><p>{text}</p><hr>'
        self.chat_display.append(formatted_message)

    def get_input_text(self):
        """Returns the text from the input box and clears it."""
        text = self.input_box.text()
        self.input_box.clear()
        return text
