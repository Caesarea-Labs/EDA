from typing import Sequence
from PySide6.QtWidgets import QMainWindow, QWidget, QLabel
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QSpacerItem
)
from PySide6.QtGui import QPalette, QFont, QResizeEvent, QCursor, QShowEvent
from PySide6.QtCore import Qt
import PySide6.QtWidgets as QtWidgets
import PySide6
from eda.ui.ui_utils import add_configurable_widget, normalize_widget, position_bottom_right, scrollable_column, set_height_absolute, set_height_relative, uiButton, uiLabel, uiRow, update_widget_pos, ConfiguredWidget


def column_widget(
    window: QMainWindow,
        x: int,
        y: int,
        width: int,
        title: str,
        children: Sequence[QWidget | ConfiguredWidget]) -> QScrollArea:



    scroll, column = scrollable_column(window, x, y, width, window.height() - 20, 
                               [(uiLabel(title, 20), {"alignment": Qt.AlignmentFlag.AlignCenter})])
    
    set_height_relative(window, scroll, 20)

    minimize_button = QPushButton("Minimize")
    minimize_button.setStyleSheet("margin-bottom: 10px;")
    def minimize_or_maximize():
        if minimize_button.text() == "Minimize":
            minimize_button.setText("Maximize")
            for child in children:
                normalized = normalize_widget(child)
                normalized[0].setVisible(False)
            set_height_absolute(scroll, 80)
        else:
            minimize_button.setText("Minimize")
            for child in children:
                normalized = normalize_widget(child)
                normalized[0].setVisible(True)
            set_height_relative(window, scroll, 20)

    minimize_button.clicked.connect(minimize_or_maximize)

    add_configurable_widget(column, minimize_button)
    for child in children:
        add_configurable_widget(column, child)

    return scroll
