# model.py

import json
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict

import os


class NoteModel(QObject):
    """
    Manages application data and business logic.
    Emits signals when data changes, allowing the View to react.
    """

    data_changed = pyqtSignal()
    settings_changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.open_files: Dict[str, str] = {}
        self.unsaved_files: set[str] = set()
        self._untitled_counter = 1
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict:
        """Loads settings from JSON, with defaults."""
        defaults = {"font_family": "Consolas", "font_size": 12}
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                defaults.update(settings)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return defaults

    def save_settings(self) -> None:
        """Saves current settings to JSON."""
        try:
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def update_setting(self, key: str, value) -> None:
        """Updates a setting and emits the settings_changed signal."""
        self.settings[key] = value
        self.save_settings()
        self.settings_changed.emit()

    def get_setting(self, key: str, default=None):
        return self.settings.get(key, default)

    def open_file(self, filepath: str) -> bool:
        """Opens a file, stores its content, and emits a signal."""
        if filepath not in self.open_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.open_files[filepath] = f.read()
                self.data_changed.emit()
                return True
            except (IOError, UnicodeDecodeError) as e:
                print(f"Error opening file {filepath}: {e}")
                return False
        return True

    def save_file(self, filepath: str, content: str) -> None:
        """Saves content to a file."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.open_files[filepath] = content
            if filepath in self.unsaved_files:
                self.unsaved_files.remove(filepath)
            self.data_changed.emit()
        except IOError as e:
            print(f"Error saving file {filepath}: {e}")

    def save_new_file(self, old_path: str, new_path: str, content: str) -> None:
        """Saves an untitled file to a new path, updating the internal state."""
        del self.open_files[old_path]
        if old_path in self.unsaved_files:
            self.unsaved_files.remove(old_path)

        self.open_files[new_path] = content
        self.save_file(new_path, content)
        self.data_changed.emit()

    def close_file(self, filepath: str) -> None:
        """Closes a file and emits a signal."""
        if filepath in self.open_files:
            del self.open_files[filepath]
            if filepath in self.unsaved_files:
                self.unsaved_files.remove(filepath)
            self.data_changed.emit()

    def create_new_file(self) -> str:
        """Creates a new, empty 'untitled' file in the model."""
        filepath = f"Untitled-{self._untitled_counter}.md"
        while filepath in self.open_files:
            self._untitled_counter += 1
            filepath = f"Untitled-{self._untitled_counter}.md"

        self.open_files[filepath] = ""
        self.unsaved_files.add(filepath)
        self._untitled_counter += 1
        self.data_changed.emit()
        return filepath

    def mark_as_unsaved(self, filepath: str) -> None:
        """Marks a file as having unsaved changes."""
        if filepath not in self.unsaved_files:
            self.unsaved_files.add(filepath)
            self.data_changed.emit()

    def update_content(self, filepath: str, content: str) -> None:
        """Updates content in memory without saving to disk."""
        if filepath in self.open_files:
            self.open_files[filepath] = content

    def rename_file(self, old_path: str, new_name: str) -> bool:
        """Renames a file on disk and updates the internal state."""
        if old_path not in self.open_files:
            return False  # Should not happen, but good to be safe

        directory = os.path.dirname(old_path)
        new_path = os.path.join(directory, new_name)

        if os.path.exists(new_path):
            print(f"Error: File '{new_path}' already exists.")
            return False

        try:
            os.rename(old_path, new_path)

            content = self.open_files.pop(old_path)
            self.open_files[new_path] = content

            if old_path in self.unsaved_files:
                self.unsaved_files.remove(old_path)
                self.unsaved_files.add(new_path)

            self.data_changed.emit()
            return True
        except OSError as e:
            print(f"Error renaming file: {e}")
            return False

    def delete_file(self, filepath: str):
        """Deletes a file from disk and closes it if it's open."""
        try:
            os.remove(filepath)
            self.close_file(filepath)
        except OSError as e:
            print(f"Error deleting file: {e}")
