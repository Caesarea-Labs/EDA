from typing import Callable, Optional, Protocol, Sequence, TypedDict, cast, runtime_checkable
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
    QScrollArea, QLayout
)
from PySide6.QtGui import QPalette, QFont, QResizeEvent, QCursor, QShowEvent
from PySide6.QtCore import Qt
import PySide6.QtWidgets as QtWidgets
import PySide6


def uiLabel(text: str, font_size: int) -> QLabel:
    label = QLabel(text)
    font = QFont()
    font.setPointSize(font_size)
    label.setFont(font)
    return label


def uiButton(text: str, on_click: Callable[[], None]) -> QPushButton:
    def click_callback():
        on_click()
    button = QPushButton(text)
    button.pressed.connect(click_callback)  # type: ignore
    return button


def uiRow(children: Sequence[QWidget]) -> QWidget:
    row_widget = QWidget()
    row_layout = QHBoxLayout(row_widget)
    row_layout.setContentsMargins(0, 0, 0, 0)

    for widget in children:
        row_layout.addWidget(widget)
    return row_widget


class WidgetLayoutConfig(TypedDict):
    alignment: Optional[Qt.AlignmentFlag]


ConfiguredWidget = tuple[QWidget, WidgetLayoutConfig]


def scrollable_column(
        window: QMainWindow,
        x: int,
        y: int,
        width: int,
        height: int,
        children: Sequence[QWidget | ConfiguredWidget]
) -> tuple[QScrollArea, QVBoxLayout]:
    # Create the scrollable area for the first column
    scroll = QScrollArea(window)
    scroll.move(x, y)
    scroll.setWidgetResizable(True)
    scroll.setFixedWidth(width)  # Adjust width as needed
    scroll.setFixedHeight(height)  # Adjust height as needed

    # Create the content widget and layout for the first scroll area
    scroll_content = QWidget(window)
    scroll.setWidget(scroll_content)
    column = QVBoxLayout(scroll_content)
    column.setSpacing(0)

    for widget in children:
        add_configurable_widget(column, widget)
    return scroll, column


def normalize_widget(widget: QWidget | ConfiguredWidget) -> ConfiguredWidget:
    if isinstance(widget, QWidget):
        return (widget, {"alignment": None})
    else:
        return widget


def add_configurable_widget(layout: QLayout, widget: QWidget | ConfiguredWidget):
    (w, config) = normalize_widget(widget)
    layout.addWidget(w)
    if config["alignment"] is not None:
        layout.setAlignment(w, config["alignment"])


@runtime_checkable
class ExtendedWidget(Protocol):
    """
    Additional properties for widgets to add basic functionallity not available in qt ("the best UI framework" hahaa)
    """
    right: Optional[int]
    """
    If specified, the element will be positioned aligned to the right, with the 'right' value being the offset
    """
    bottom: Optional[int]
    """
    If specified, the element will be positioned aligned to the bottom, with the 'bottom' value being the offset
    """
    relative_height_reduction: Optional[int]
    """
    If specified, the widget will have this much height less than the screen height. 
    """


def position_bottom_right(window: QMainWindow, widget: QWidget, bottom: int, right: int):
    extended = cast(ExtendedWidget, widget)
    extended.right = right
    extended.bottom = bottom
    extended.relative_height_reduction = None
    update_widget_pos(window, widget)


def set_height_relative(window: QMainWindow, widget: QWidget, relative_height_reduction: int):
    extended = cast(ExtendedWidget, widget)
    extended.relative_height_reduction = relative_height_reduction
    extended.right = None
    extended.bottom = None
    widget.setFixedHeight(window.height() - relative_height_reduction)

def set_height_absolute(widget: QWidget, height: int):
    extended = cast(ExtendedWidget, widget)
    extended.relative_height_reduction = None
    widget.setFixedHeight(height)


def update_widget_pos(window: QMainWindow, widget: QWidget):
    """
    Must be called on screen resize on ExtendedWidgets
    """
    if isinstance(widget, ExtendedWidget):
        right = widget.right or 0
        bottom = widget.bottom or 0
        if widget.right is not None and widget.bottom is not None:
            widget.move(window.width() - right - widget.width(), window.height() - bottom - widget.height())
        if widget.relative_height_reduction is not None:
            widget.setFixedHeight(window.height() - widget.relative_height_reduction)
