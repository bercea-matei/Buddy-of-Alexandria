# controller.py

import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QApplication, QInputDialog
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont


from view.SettingsDialog import SettingsDialog
from view.LiveMarkdownEditor import LiveMarkdownEditor

from controller.AIWorker import AIWorker


class Controller(QObject):
    """Connects the Model and the View."""

    start_ai_query = pyqtSignal(str)

    def __init__(self, model, view, index_manager) -> None:
        super().__init__()
        self._model = model
        self._view = view
        self._index_manager = index_manager
        self._current_font = self.get_font_from_settings()
        if hasattr(self._view, "chat_widget"):
            self._view.chat_widget.controller = self

        self._view.open_folder_action.triggered.connect(self.open_folder)
        self._view.new_file_action.triggered.connect(self.new_file)
        self._view.save_file_action.triggered.connect(self.save_current_file)
        self._view.settings_action.triggered.connect(self.open_settings)
        self._view.file_tree.doubleClicked.connect(self.on_file_tree_dclick)
        self._view.tab_widget.tabCloseRequested.connect(self.close_tab)
        self._view.rename_file_action.triggered.connect(self.rename_current_file)
        self._view.delete_file_action.triggered.connect(self.delete_current_file)

        self._model.data_changed.connect(self.on_model_data_changed)
        self._model.settings_changed.connect(self.on_model_settings_changed)

        self.ai_thread = QThread()
        self.ai_worker = AIWorker(self._index_manager)
        self.ai_worker.moveToThread(self.ai_thread)

        self.start_ai_query.connect(self.ai_worker.run_query)
        self.ai_worker.result_ready.connect(self.handle_ai_response)
        self.ai_worker.error_occurred.connect(self.handle_ai_error)
        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(self.cleanup_thread)

        self.ai_thread.start()

    def __del__(self) -> None:
        self.cleanup_thread()

    def show(self) -> None:
        """Display everything"""
        self._view.show()

    def open_folder(self) -> None:
        """Open a folder Menu"""
        path = QFileDialog.getExistingDirectory(self._view, "Open Folder")
        if path:
            self._view.set_file_tree_root(path)

    def new_file(self) -> None:
        """Create a new file"""
        new_path = self._model.create_new_file()
        self.focus_tab(new_path)

    def rename_current_file(self):
        filepath = self._view.get_current_filepath()
        if not filepath:
            return

        current_name = os.path.basename(filepath)
        new_name, ok = QInputDialog.getText(
            self._view, "Rename File", "Enter new name:", text=current_name
        )

        if ok and new_name and new_name != current_name:
            if not new_name.endswith(".md"):
                new_name += ".md"

            if not self._model.rename_file(filepath, new_name):
                QMessageBox.warning(
                    self._view,
                    "Rename Failed",
                    f"Could not rename to '{new_name}'. The file may already exist.",
                )

    def delete_current_file(self):
        filepath = self._view.get_current_filepath()
        if not filepath:
            return  # No file is open

        filename = os.path.basename(filepath)
        reply = QMessageBox.question(
            self._view,
            "Confirm Delete",
            f"Are you sure you want to permanently delete '{filename}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._model.delete_file(filepath)

    def open_settings(self) -> None:
        """Open Settings menu"""
        dialog = SettingsDialog(self._model.settings, self._view)
        if dialog.exec():
            new_settings = dialog.get_settings()
            for key, value in new_settings.items():
                self._model.update_setting(key, value)

    def on_file_tree_dclick(self, index) -> None:
        """Open notes from left menu"""
        filepath = self._view.file_model.filePath(index)
        if os.path.isfile(filepath) and filepath.endswith(".md"):
            self._model.open_file(filepath)
            self.focus_tab(filepath)

    def close_tab(self, index) -> None:
        """Menu for managing tab closing"""
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

    def on_model_data_changed(self) -> None:
        """Update the tabs in the view to reflect the model's state."""
        open_files = self._model.open_files
        current_tabs = {
            self._view.tab_widget.widget(i).filepath: i
            for i in range(self._view.tab_widget.count())
        }

        for path in set(current_tabs.keys()) - set(open_files.keys()):
            self._view.tab_widget.removeTab(current_tabs[path])

        for path, content in open_files.items():
            title = os.path.basename(path)
            if path in self._model.unsaved_files:
                title += "*"

            if path not in current_tabs:
                editor_widget = LiveMarkdownEditor(path, self._current_font)
                editor_widget.set_content(content)

                editor_widget.textChanged.connect(
                    lambda p=path: self.on_editor_text_changed(p)
                )

                self._view.tab_widget.addTab(editor_widget, title)
                self._view.tab_widget.setTabToolTip(
                    self._view.tab_widget.count() - 1, path
                )
            else:
                index = current_tabs[path]
                self._view.tab_widget.setTabText(index, title)

    def on_editor_text_changed(self, filepath) -> None:
        """
        When user types, get content from the active widget,
        update model, and mark as unsaved.
        """
        current_widget = self._view.tab_widget.currentWidget()

        if current_widget and current_widget.filepath == filepath:
            content = current_widget.get_content()
            self._model.update_content(filepath, content)
            self._model.mark_as_unsaved(filepath)

    def save_current_file(self) -> None:
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
                self._index_manager.update_file_node(new_filepath)
        else:
            self._model.save_file(filepath, content)
            self._index_manager.update_file_node(filepath)

    def on_model_settings_changed(self) -> None:
        """Apply new settings to the application."""
        self._current_font = self.get_font_from_settings()
        for i in range(self._view.tab_widget.count()):
            tab = self._view.tab_widget.widget(i)
            if isinstance(tab, LiveMarkdownEditor):
                tab.setFont(self._current_font)
                tab.update_highlighter_formats()

    def get_font_from_settings(self) -> QFont:
        """Get the font the app is using"""
        family = self._model.get_setting("font_family", "Consolas")
        size = self._model.get_setting("font_size", 12)
        return QFont(family, size)

    def focus_tab(self, filepath) -> None:
        """Sets the currently visible tab to the one
        with the given filepath."""
        for i in range(self._view.tab_widget.count()):
            if self._view.tab_widget.widget(i).filepath == filepath:
                self._view.tab_widget.setCurrentIndex(i)
                break

    def get_initial_font(self) -> None:
        """Returns the font created from the initial settings."""
        return self._current_font

    def save_all_unsaved_files(self) -> None:
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

    def handle_exit_request(self, event) -> None:
        """
        Called by the View's closeEvent. Determines if the app should close.
        """
        if not self._model.unsaved_files:
            event.accept()
            return

        dialog = QMessageBox(self._view)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setText("You have unsaved changes.")
        dialog.setInformativeText("Do you want to save your changes before exiting?")
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.Save)

        user_choice = dialog.exec()

        if user_choice == QMessageBox.StandardButton.Save:
            self.save_all_unsaved_files()
            event.accept()
        elif user_choice == QMessageBox.StandardButton.Discard:
            event.accept()
        else:
            event.ignore()

    def cleanup_thread(self) -> None:
        """Safely stops the worker thread."""
        if self.ai_thread.isRunning():
            print("Quitting AI worker thread...")
            self.ai_thread.quit()
            self.ai_thread.wait()  # Wait for the thread to fully stop
            print("AI worker thread finished.")

    def handle_send_chat_message(self) -> None:
        """
        Slot that is called when the user clicks 'Send' or presses Enter.
        """
        chat_widget = self._view.chat_widget
        user_text = chat_widget.get_input_text()

        if not user_text.strip():
            return
        chat_widget.add_message("User", user_text)
        chat_widget.add_message("BoA", "Hmm...")

        self.start_ai_query.emit(user_text)

    @pyqtSlot(str)
    def handle_ai_response(self, ai_text) -> None:
        """
        This slot runs in the main GUI thread, so it's safe to update the UI.
        """
        chat_widget = self._view.chat_widget
        chat_widget.add_message("BoA", ai_text)

    @pyqtSlot(str)
    def handle_ai_error(self, error_message) -> None:
        """Handles any errors that occurred in the worker thread."""
        chat_widget = self._view.chat_widget
        chat_widget.add_message("System", f"An error occurred: {error_message}")
