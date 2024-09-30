import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QWidget,
    QHBoxLayout, QSpacerItem, QSizePolicy
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("List Anchored to Right Edge")
        self.resize(600, 400)  # Set initial size

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create the list widget
        list_widget = QListWidget()
        for i in range(10):
            list_widget.addItem(f"Item {i+1}")

        # Create a horizontal layout
        layout = QHBoxLayout()

        # Add a stretchable spacer to the layout
        spacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        layout.addItem(spacer)

        # Add the list widget to the layout
        layout.addWidget(list_widget)

        # Set the layout to the central widget
        central_widget.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
