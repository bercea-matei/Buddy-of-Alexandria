# controller.py

import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QFont

from view.SettingsDialog import SettingsDialog
from view.LiveMarkdownEditor import LiveMarkdownEditor


class Controller(QObject):
    """Connects the Model and the View."""

    def __init__(self, model, view):
        super().__init__()
        self._model = model
        self._view = view
        self._current_font = self.get_font_from_settings()

        # Connect signals from view to controller slots
        self._view.open_folder_action.triggered.connect(self.open_folder)
        self._view.new_file_action.triggered.connect(self.new_file)
        self._view.save_file_action.triggered.connect(self.save_current_file)
        self._view.settings_action.triggered.connect(self.open_settings)
        self._view.file_tree.doubleClicked.connect(self.on_file_tree_dclick)
        self._view.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Connect signals from model to view/controller slots
        self._model.data_changed.connect(self.on_model_data_changed)
        self._model.settings_changed.connect(self.on_model_settings_changed)

    def show(self):
        self._view.show()

    def open_folder(self):
        path = QFileDialog.getExistingDirectory(self._view, "Open Folder")
        if path:
            self._view.set_file_tree_root(path)

    def new_file(self):
        new_path = self._model.create_new_file()
        self.focus_tab(new_path)

    def open_settings(self):
        dialog = SettingsDialog(self._model.settings, self._view)
        if dialog.exec():
            new_settings = dialog.get_settings()
            for key, value in new_settings.items():
                self._model.update_setting(key, value)

    def on_file_tree_dclick(self, index):
        filepath = self._view.file_model.filePath(index)
        if os.path.isfile(filepath) and filepath.endswith(".md"):
            self._model.open_file(filepath)
            self.focus_tab(filepath)

    def close_tab(self, index):
        filepath = self._view.tab_widget.widget(index).filepath
        if filepath in self._model.unsaved_files:
            reply = QMessageBox.question(
                self._view,
                "Unsaved Changes",
                f"'{os.path.basename(filepath)}' has unsaved changes."
                + "Do you want to close it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self._model.close_file(filepath)

    def on_model_data_changed(self):
        """Update the tabs in the view to reflect the model's state."""
        open_files = self._model.open_files
        current_tabs = {
            self._view.tab_widget.widget(i).filepath: i
            for i in range(self._view.tab_widget.count())
        }

        # Close tabs no longer in model
        for path in set(current_tabs.keys()) - set(open_files.keys()):
            self._view.tab_widget.removeTab(current_tabs[path])

        # Add or update tabs
        for path, content in open_files.items():
            title = os.path.basename(path)
            if path in self._model.unsaved_files:
                title += "*"  # Initiative: Mark unsaved files

            if path not in current_tabs:
                editor_widget = LiveMarkdownEditor(path, self._current_font)
                editor_widget.set_content(content)

                # Connect the textChanged signal to update the model
                editor_widget.textChanged.connect(
                    lambda p=path: self.on_editor_text_changed(p)
                )

                self._view.tab_widget.addTab(editor_widget, title)
                self._view.tab_widget.setTabToolTip(
                    self._view.tab_widget.count() - 1, path
                )
            else:  # Update existing tab title (e.g., for unsaved marker)
                index = current_tabs[path]
                self._view.tab_widget.setTabText(index, title)

    def on_editor_text_changed(self, filepath):
        """
        When user types, get content from the active widget,
        update model, and mark as unsaved.
        """
        current_widget = self._view.tab_widget.currentWidget()
        # Ensure we're not getting a signal from a tab that is not in focus
        if current_widget and current_widget.filepath == filepath:
            content = current_widget.get_content()
            self._model.update_content(filepath, content)
            self._model.mark_as_unsaved(filepath)

    def save_current_file(self):
        """Saving is now simple and synchronous again."""
        filepath = self._view.get_current_filepath()
        if not filepath:
            return

        current_tab = self._view.tab_widget.currentWidget()
        content = current_tab.get_content()

        if filepath.startswith("Untitled-"):
            new_filepath, _ = QFileDialog.getSaveFileName(
                self._view, "Save File", filepath, "Markdown Files (*.md)"
            )
            if new_filepath:
                self._model.save_new_file(filepath, new_filepath, content)
        else:
            self._model.save_file(filepath, content)

    def on_model_settings_changed(self):
        """Apply new settings to the application."""
        self._current_font = self.get_font_from_settings()
        for i in range(self._view.tab_widget.count()):
            tab = self._view.tab_widget.widget(i)
            if isinstance(tab, LiveMarkdownEditor):
                tab.setFont(self._current_font)
                tab.update_highlighter_formats()

    def get_font_from_settings(self):
        family = self._model.get_setting("font_family", "Consolas")
        size = self._model.get_setting("font_size", 12)
        return QFont(family, size)

    def focus_tab(self, filepath):
        """Sets the currently visible tab to the one
        with the given filepath."""
        for i in range(self._view.tab_widget.count()):
            if self._view.tab_widget.widget(i).filepath == filepath:
                self._view.tab_widget.setCurrentIndex(i)
                break

    def get_initial_font(self):
        """Returns the font created from the initial settings."""
        return self._current_font

    def save_all_unsaved_files(self):
        """Iterate through all unsaved files and save their content."""
        for filepath in list(self._model.unsaved_files):
            if filepath.startswith("Untitled-"):
                if self._view.get_current_filepath() == filepath:
                    self.save_current_file()
                continue

            tab_widget = self._view.get_tab_by_filepath(filepath)
            if tab_widget:
                content = tab_widget.get_content()
                self._model.save_file(filepath, content)

    def handle_exit_request(self, event):
        """
        Called by the View's closeEvent. Determines if the app should close.
        """
        if not self._model.unsaved_files:
            # If there are no unsaved changes, accept the event and close.
            event.accept()
            return

        # There are unsaved changes, so we must ask the user.
        dialog = QMessageBox(self._view)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setText("You have unsaved changes.")
        dialog.setInformativeText(
            "Do you want to save your" + "changes before exiting?"
        )
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.Save)

        user_choice = dialog.exec()

        if user_choice == QMessageBox.StandardButton.Save:
            # User wants to save.
            self.save_all_unsaved_files()
            event.accept()  # Proceed with closing
        elif user_choice == QMessageBox.StandardButton.Discard:
            # User doesn't want to save.
            event.accept()  # Proceed with closing
        else:  # Cancel
            # User cancelled the exit.
            event.ignore()  # Abort the close operation
