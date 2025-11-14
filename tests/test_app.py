import os

from model.NotesModel import NoteModel
from view.MainView import MainView
from controller.controller import Controller


# --- Test 1: The "Dummy" Test ---
def test_app_instantiation(qtbot):
    """
    Tests if the main MVC components can be created without raising an exception.
    """
    model = NoteModel()
    view = MainView()
    controller = Controller(model, view)
    view.controller = controller

    assert model is not None
    assert view is not None
    assert controller is not None
    print("App components instantiated successfully.")


# --- Test 2: A Test for a Core Feature ---
def test_new_file_action_updates_model_and_view(qtbot):
    """
    Tests if triggering the 'New File' action correctly updates
    both the Model and the View, demonstrating the full MVC loop.
    """
    model = NoteModel()
    view = MainView()
    controller = Controller(model, view)
    view.controller = controller

    view.new_file_action.trigger()

    assert len(model.open_files) == 1
    assert "Untitled-1.md" in model.open_files
    assert model.open_files["Untitled-1.md"] == ""

    assert view.tab_widget.count() == 1
    first_tab_title = view.tab_widget.tabText(0)
    assert first_tab_title == "Untitled-1.md*"

    assert os.path.basename(view.get_current_filepath()) == "Untitled-1.md"
    print("New file action correctly updated model and view.")
