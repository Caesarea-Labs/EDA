from dataclasses import dataclass
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
import pyvista as pv
from pyvistaqt import BackgroundPlotter, QtInteractor

from .layout_plot import plot_layout

from ..layout import Layout
from ..test_layout import test_layout_const





class MainWindow(QMainWindow):
    c_layout: Layout

    def __init__(self, layout: Layout):
        super().__init__()
        self.c_layout = layout
        # plot_layout_with_gui()

        # Add a mesh to the plotter
        self.plotter = QtInteractor(self)
        # Set up the central widget as the PyVista plotter
        self.setCentralWidget(self.plotter)

        # Create the scrollable area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(200)  # Adjust width as needed
        scroll.setFixedHeight(400)  # Adjust height as needed

        # Create the content widget and layout for the scroll area
        scroll_content = QWidget()
        scroll.setWidget(scroll_content)
        column = QVBoxLayout(scroll_content)

        # Add 20 rows with a button and text label
        for i in range(1, 21):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)

            button = QPushButton(f"Button {i}")
            label = QLabel(f"Text {i}")

            row_layout.addWidget(button)
            row_layout.addWidget(label)
            row_layout.addStretch()  # Optional: Add stretch to push items to the left

            column.addWidget(row_widget)

        # scroll.setAlignment(Qt.AlignmentFlag.AlignRight)
        # column.addStretch()
        scroll.raise_()
        # Position the scroll area in the top-right corner
        # self.scroll_area.move(self.width() - self.scroll_area.width(), 0)
        # self.scroll_area.raise_()  # Bring the scroll area to the front

        # Update the position of the scroll area when the window is resized
        # self.resizeEvent = self.on_resize

        plot_layout(self.c_layout, show_text=False, plotter=self.plotter)
        sys.exit()


        # sphere = pv.Sphere()

        # plotter = BackgroundPlotter()
        # plotter.add_mesh(sphere)

        # mesh = pv.Sphere()
        # self.plotter.add_mesh(mesh)
        # self.plotter.show()

    # def on_resize(self, event):
    #     """Reposition scroll area on window resize."""
    #     self.scroll_area.move(self.width() - self.scroll_area.width(), 0)
    #     event.accept()



def plot_layout_with_qt_gui(layout: Layout):
    app = QApplication(sys.argv)
    window = MainWindow(layout)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    plot_layout_with_qt_gui(test_layout_const)
    # plot_layout_with_gui(get_large_gds_layout_test())
    # app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec())