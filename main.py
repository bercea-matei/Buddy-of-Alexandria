# main.py

import sys
from PyQt6.QtWidgets import QApplication
from model.model import NoteModel
from view.MainView import MainView
from controller.controller import Controller


if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = NoteModel()
    view = MainView()
    controller = Controller(model, view)
    view.set_controller(controller)

    controller.on_model_settings_changed()

    controller.show()
    sys.exit(app.exec())
