# main.py

from view.MainView import MainView
from controller.controller import Controller
from model.IndexManager import IndexManager
from model.AiConfig import full_local_ai_config

import sys
from PyQt6.QtWidgets import QApplication
from model.NotesModel import NoteModel
from pathlib import Path
from platformdirs import user_documents_dir
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)

    docs_directory = os.path.join(Path(user_documents_dir()), "BoA")
    if not full_local_ai_config():
        print("\nAn Error occurred during ai config, the app cannot start.")

    model = NoteModel()
    view = MainView()
    index_manager = IndexManager(docs_directory)
    controller = Controller(model, view, index_manager)
    view.set_controller(controller)

    controller.on_model_settings_changed()

    controller.show()
    sys.exit(app.exec())
