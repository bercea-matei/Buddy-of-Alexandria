import sys
from PyQt6.QtWidgets import QApplication


def test_app_instantiation():
    """
    Tests if the main components can be created.
    This is a basic "smoke test".
    """
    from model.NotesModel import NoteModel
    from view.MainView import MainView
    from controller.controller import Controller

    app = QApplication.instance() or QApplication(sys.argv)

    model = NoteModel()
    view = MainView()
    controller = Controller(model, view)
    view.controller = controller

    assert model is not None
    assert view is not None
    assert controller is not None
    assert app is not None
