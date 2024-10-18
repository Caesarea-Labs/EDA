import sys
from tkinter import Widget
from typing import Any, Optional, Protocol, cast, runtime_checkable
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
)
from PySide6.QtGui import QPalette, QFont, QResizeEvent, QCursor, QShowEvent
from PySide6.QtCore import Qt
import PySide6.QtWidgets as QtWidgets
from pyvistaqt import QtInteractor
import pyvista as pv

from eda.layout import Layout
from eda.ui.hover_callback import on_world_hover
from eda.ui.layout_plot import MeshGroup, add_layout_elements_to_plot
from tests.test_layout import test_layout_const


class MainWindow(QMainWindow):
    c_layout: Layout

    def showEvent(self, event: QShowEvent):
        self.showMaximized()

    def __init__(self, layout: Layout):
        super().__init__()
        self.c_layout = layout

        # Add a mesh to the plotter
        self.plotter = QtInteractor(self)  # type: ignore
        # Set up the central widget as the PyVista plotter
        self.setCentralWidget(self.plotter)

        # Create the scrollable area
        scroll = QScrollArea(self)
        scroll.move(10, 10)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(200)  # Adjust width as needed
        scroll.setFixedHeight(self.height() - 20)  # Adjust height as needed

        self.scroller = scroll

        # Create the content widget and layout for the scroll area
        scroll_content = QWidget(self)
        scroll.setWidget(scroll_content)
        column = QVBoxLayout(scroll_content)
        column.setSpacing(0)



        bindings = add_layout_elements_to_plot(self.c_layout, show_text=False, plotter=self.plotter)

        # Need to wrap the text in something for it to work
        cursor_pos = QScrollArea(self)
        cursor_pos.setStyleSheet("QScrollArea { background-color: white; }")
        self.position_bottom_right(cursor_pos, 5, 5)
        self.cursor_pos = cursor_pos
        cursor_pos.setFixedHeight(30)

        self.cursor_pos_text = QLabel("(0000.00, 0000.00, 0000.00)", cursor_pos)
        self.cursor_pos_text.setStyleSheet("QLabel { color: black }")
        cursor_pos.adjustSize()

        def update_cursor_position(pos: tuple[float, float, float]):
            self.cursor_pos_text.setText(f"{round(pos[0], 2)}, {round(pos[1], 2)}, {round(pos[2], 2)}")
            self.cursor_pos_text.adjustSize()
        on_world_hover(self.plotter, update_cursor_position)

        checkboxes: dict[str, QtWidgets.QCheckBox] = {}
        def show_all():
            for checkbox in checkboxes.values():
                checkbox.setChecked(True)
        show_all_button = QPushButton("Show All")
        show_all_button.pressed.connect(show_all)
        column.addWidget(show_all_button)

        # Add 20 rows with a button and text label
        for group_name, group in bindings.mesh_groups.items():
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)

            focus_button = QPushButton(text="Focus")
            # The first parameter is passed by QT so we need to ignore it

            def focus_signal(_: bool, focus_group_name: str = group_name):
                for iter_group_name, checkbox in checkboxes.items():
                    # Set others to 0, this one to 1
                    checkbox.setChecked(iter_group_name == focus_group_name)

            focus_button.clicked.connect(focus_signal)

            label = QLabel(group_name)
            font = QFont()
            font.setPointSize(20)
            label.setFont(font)

            row_layout.addWidget(focus_button)
            checkbox = signal_checkbox(self.plotter, group)
            checkboxes[group_name] = checkbox
            row_layout.addWidget(checkbox)
            row_layout.addWidget(label)
            row_layout.addStretch()  # Add stretch to push items to the left

            column.addWidget(row_widget)

    def resizeEvent(self, event: QResizeEvent):
        # Set the label's height to match the app's height
        self.scroller.setFixedHeight(self.height() - 20)
        self.update_widget_pos(self.cursor_pos)
        return super().resizeEvent(event)

    def position_bottom_right(self, widget: QWidget, bottom: int, right: int):
        extended = cast(ExtendedWidget, widget)
        extended.right = right
        extended.bottom = bottom
        self.update_widget_pos(widget)

    def update_widget_pos(self, widget: QWidget):
        if isinstance(widget, ExtendedWidget):
            right = widget.right or 0
            bottom = widget.bottom or 0
            if widget.right is not None and widget.bottom is not None:
                widget.move(self.width() - right - widget.width(), self.height() - bottom - widget.height())


def plot_layout_with_qt_gui(layout: Layout):
    app = QApplication(sys.argv)
    window = MainWindow(layout)
    window.show()
    sys.exit(app.exec())


def signal_checkbox(plotter: pv.Plotter, group: MeshGroup) -> QtWidgets.QCheckBox:
    checkbox = QtWidgets.QCheckBox()
    checkbox.setChecked(True)
    color = group['color']

    def on_checkbox_state_changed(state: int, actor: pv.Actor = group['actor']):
        if state == 0:
            plotter.remove_actor(actor, render = False) # type: ignore
        else:
            plotter.add_actor(actor, render = False) # type: ignore

    checkbox.stateChanged.connect(on_checkbox_state_changed)
    checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
    checkbox.setStyleSheet(f"""
    /* Set the size of the checkbox indicator */
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
    }}

    /* Style for the unchecked state */
    QCheckBox::indicator:unchecked {{
        background-color: gray;
        border: 2px solid {color};
    }}

    /* Style for the checked state */
    QCheckBox::indicator:checked {{
        background-color: {color};
        border: 2px solid {color};
    }}

    /* Optional: Style for the hover state */
    QCheckBox::indicator:hover {{
        border: 2px solid blue;
    }}
""")
    return checkbox


def add_border_to_widgets(widget: QWidget, color: str = "red", thickness: int = 2):
    """
    Recursively adds a colored border to every child widget.

    :param widget: The parent widget (or main window) containing child widgets.
    :param color: The color of the border (default is red).
    :param thickness: The thickness of the border (default is 2px).
    """
    # Add a border to the current widget
    widget.setStyleSheet(f"border: {thickness}px solid {color};")

    # Find all children and apply the same border
    for child in widget.findChildren(QWidget):
        child.setStyleSheet(f"border: {thickness}px solid {color};")


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


if __name__ == "__main__":
    plot_layout_with_qt_gui(test_layout_const)
    # plot_layout_with_gui(get_large_gds_layout_test())
    # app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec())
