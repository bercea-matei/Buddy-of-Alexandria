# main.py

import sys
from PyQt6.QtWidgets import QApplication
from model import NoteModel
from view import MainView
from controller import Controller


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Pre-warming is no longer needed.

    model = NoteModel()
    view = MainView()
    controller = Controller(model, view)

    view.controller = controller

    controller.on_model_settings_changed()

    controller.show()
    sys.exit(app.exec())
