# main.py

from view.MainView import MainView
from controller.controller import Controller
from model.IndexManager import IndexManager

import sys
from PyQt6.QtWidgets import QApplication
from model.NotesModel import NoteModel
from pathlib import Path
from platformdirs import user_documents_dir
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)

    docs_directory = os.path.join(Path(user_documents_dir()), "BoA")

    is_ci_environment = os.environ.get("CI") == "true"
    ai_is_running = False
    if is_ci_environment:
        print("CI Environment detected. Skipping Ollama startup checks.")
        ai_is_running = False
    else:
        # if not full_local_ai_config():
        # print("Critical Error: Could not start AI backend. +
        # starting in minimal mode.")
        # else
        # ai_is_running = True
        pass

    model = NoteModel()
    view = MainView()
    index_manager = IndexManager(docs_directory)
    controller = Controller(model, view, index_manager, ai_is_running)
    view.set_controller(controller)

    controller.on_model_settings_changed()

    controller.show()
    sys.exit(app.exec())
