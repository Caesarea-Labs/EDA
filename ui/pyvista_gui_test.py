import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
import pyvista as pv
from pyvistaqt import QtInteractor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Add a mesh to the plotter
        self.plotter = QtInteractor(self)
        # Set up the central widget as the PyVista plotter
        self.setCentralWidget(self.plotter)

        # Create the scrollable area
        scroll = scroll_area = QScrollArea(self)
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


        mesh = pv.Sphere()
        self.plotter.add_mesh(mesh)
        self.plotter.show()

    # def on_resize(self, event):
    #     """Reposition scroll area on window resize."""
    #     self.scroll_area.move(self.width() - self.scroll_area.width(), 0)
    #     event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
