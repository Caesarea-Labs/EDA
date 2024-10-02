import sys
from typing import Any
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
from PySide6.QtGui import QPalette, QFont, QResizeEvent, QCursor
from PySide6.QtCore import Qt
import PySide6.QtWidgets as QtWidgets
from pyvistaqt import QtInteractor
import pyvista as pv

from eda.layout import Layout
from eda.ui.layout_plot import MeshGroup, plot_layout
from eda.test_layout import test_layout_const


class MainWindow(QMainWindow):
    c_layout: Layout

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

        bindings = plot_layout(self.c_layout, show_text=False, plotter=self.plotter)

        checkboxes: dict[str, QtWidgets.QCheckBox] = {}

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


            # palette = button.palette()
            # palette.setColor(QPalette.)
            # button.setPalette(palette)
            label = QLabel(group_name)
            font = QFont()
            font.setPointSize(20)
            label.setFont(font)

            row_layout.addWidget(focus_button)
            checkbox  = signal_checkbox(group)
            checkboxes[group_name] = checkbox
            row_layout.addWidget(checkbox)
            row_layout.addWidget(label)
            row_layout.addStretch()  # Add stretch to push items to the left

            column.addWidget(row_widget)

        # add_border_to_widgets(scroll)

    def resizeEvent(self, event: QResizeEvent):
        # Set the label's height to match the app's height
        self.scroller.setFixedHeight(self.height() - 20)
        return super().resizeEvent(event)


def plot_layout_with_qt_gui(layout: Layout):
    app = QApplication(sys.argv)
    window = MainWindow(layout)
    window.show()
    sys.exit(app.exec())

def signal_checkbox(group: MeshGroup)-> QtWidgets.QCheckBox:
    checkbox = QtWidgets.QCheckBox()
    checkbox.setChecked(True)
    color = group['color']

    def on_checkbox_state_changed(state: int, actor: pv.Actor =group['actor']):
        # State is 0 (unchecked), 2 (checked), or 1 (partially checked)
        # if state == 0:
        actor.SetVisibility(0 if state == 0 else 1)
        # elif state == 2:
        #     label.setText("Checkbox is checked")

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


if __name__ == "__main__":
    plot_layout_with_qt_gui(test_layout_const)
    # plot_layout_with_gui(get_large_gds_layout_test())
    # app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec())
