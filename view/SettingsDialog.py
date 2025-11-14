# SettingsDialog.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QDialog,
    QFormLayout,
    QFontComboBox,
    QSpinBox,
    QDialogButtonBox,
    QScrollArea,
)
from PyQt6.QtGui import (
    QFont,
)


class SettingsDialog(QDialog):
    """A scrollable settings dialog."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)

        form_layout = QFormLayout(container)

        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setCurrentFont(QFont(settings.get("font_family")))
        form_layout.addRow("Font Family:", self.font_family_combo)

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(72)
        self.font_size_spinbox.setValue(settings.get("font_size", 12))
        form_layout.addRow("Font Size:", self.font_size_spinbox)

        # Add more settings here in the future

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_settings(self):
        return {
            "font_family": self.font_family_combo.currentFont().family(),
            "font_size": self.font_size_spinbox.value(),
        }
