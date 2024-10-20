import sys
from tkinter import Widget
from typing import Any, Optional, Protocol, Sequence, cast, runtime_checkable
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
from eda.ui.plottable import Plottable
from eda.ui.hover_callback import on_world_hover
from eda.ui.layout_plot import LayoutPlotBindings, MeshGroup, plot_meshes
from eda.ui.ui_components import column_widget
from eda.ui.ui_utils import position_bottom_right, scrollable_column, uiButton, uiLabel, uiRow, update_widget_pos, ConfiguredWidget


class MainWindow(QMainWindow):
    c_layout: Plottable

    def showEvent(self, event: QShowEvent):
        self.showMaximized()

    def __init__(self, layout: Plottable, show_polygon_names: bool):
        super().__init__()
        self.c_layout = layout

        # Add a mesh to the plotter
        self.plotter = QtInteractor(self)  # type: ignore
        # Set up the central widget as the PyVista plotter
        self.setCentralWidget(self.plotter)
        bindings = plot_meshes(self.c_layout.to_meshes(), show_text=show_polygon_names, plotter=self.plotter)

        self.pointer_coords()
        self.signal_select_column(bindings)

    def pointer_coords(self):

        # Need to wrap the text in something for it to work
        cursor_pos = QScrollArea(self)
        cursor_pos.setStyleSheet("QScrollArea { background-color: white; }")
        position_bottom_right(self, cursor_pos, 5, 5)
        self.cursor_pos = cursor_pos
        cursor_pos.setFixedHeight(30)

        self.cursor_pos_text = QLabel("(0000.00, 0000.00, 0000.00)", cursor_pos)
        self.cursor_pos_text.setStyleSheet("QLabel { color: black }")
        cursor_pos.adjustSize()

        def update_cursor_position(pos: tuple[float, float, float]):
            self.cursor_pos_text.setText(f"{round(pos[0], 2)}, {round(pos[1], 2)}, {round(pos[2], 2)}")
            self.cursor_pos_text.adjustSize()
        on_world_hover(self.plotter, update_cursor_position)

    def signal_select_column(self, bindings: LayoutPlotBindings):
        def show_all():
            for checkbox in checkboxes.values():
                checkbox.setChecked(True)

        scroll_children: list[QWidget] = [
            uiButton("Show All", show_all)
        ]

        checkboxes: dict[str, QtWidgets.QCheckBox] = {}

        # Add 20 rows with a button and text label to the first column
        for group_name, group in bindings.mesh_groups.items():
            checkbox = signal_checkbox(self.plotter, group)
            checkboxes[group_name] = checkbox

            # The first parameter is passed by QT so we need to ignore it
            def focus_signal(focus_group_name: str = group_name):
                for iter_group_name, checkbox in checkboxes.items():
                    # Set others to 0, this one to 1
                    checkbox.setChecked(iter_group_name == focus_group_name)

            row_widget = uiRow(
                [
                    uiButton("Focus", focus_signal),
                    checkbox,
                    uiLabel(group_name, 20)
                ]
            )

            scroll_children.append(row_widget)

        self.scroller1 = column_widget(self, x=10, y=10, width=200,title="Signals" , children=scroll_children)

    # def layer_select_column(self, bindings: LayoutPlotBindings):
    #     def show_all():
    #         for checkbox in checkboxes.values():
    #             checkbox.setChecked(True)

    #     scroll_children: list[QWidget] = [
    #         uiButton("Show All", show_all)
    #     ]

    #     checkboxes: dict[str, QtWidgets.QCheckBox] = {}

    #     # Add 20 rows with a button and text label to the first column
    #     for group_name, group in bindings.mesh_groups.items():
    #         checkbox = signal_checkbox(self.plotter, group)
    #         checkboxes[group_name] = checkbox

    #         # The first parameter is passed by QT so we need to ignore it
    #         def focus_layer(focus_group_name: str = group_name):
    #             for iter_group_name, checkbox in checkboxes.items():
    #                 # Set others to 0, this one to 1
    #                 checkbox.setChecked(iter_group_name == focus_group_name)

    #         row_widget = uiRow(
    #             [
    #                 uiButton("Focus", focus_layer),
    #                 checkbox,
    #                 uiLabel(group_name, 20)
    #             ]
    #         )

    #         scroll_children.append(row_widget)

    #     self.scroller2 = column_widget(self, x=210, y=10, width=200,title="Layers" , children=scroll_children)





    def resizeEvent(self, event: QResizeEvent):
        # Set the label's height to match the app's height
        # self.scroller1.setFixedHeight(self.height() - 20)
        # self.scroller2.setFixedHeight(self.height() - 20)
        update_widget_pos(self, self.cursor_pos)
        update_widget_pos(self, self.scroller1)
        # update_widget_pos(self, self.scroller2)
        return super().resizeEvent(event)

    # def position_bottom_right(self, widget: QWidget, bottom: int, right: int):
    #     extended = cast(ExtendedWidget, widget)
    #     extended.right = right
    #     extended.bottom = bottom
    #     self.update_widget_pos(widget)


def plot_layout_with_qt_gui(layout: Plottable, show_polygon_names: bool = False):
    app = QApplication(sys.argv)
    window = MainWindow(layout, show_polygon_names)
    window.show()
    app.exec()
    



def signal_checkbox(plotter: pv.Plotter, group: MeshGroup) -> QtWidgets.QCheckBox:
    checkbox = QtWidgets.QCheckBox()
    checkbox.setChecked(True)
    color = group['color']

    def on_checkbox_state_changed(state: int, actor: pv.Actor = group['actor']):
        if state == 0:
            plotter.remove_actor(actor, render=False)  # type: ignore
        else:
            plotter.add_actor(actor, render=False)  # type: ignore

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
