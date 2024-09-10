import tkinter as tk
from tkinter import filedialog
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class PolygonDrawer:
    def __init__(self, master):
        self.master = master
        self.master.title("2D Polygon Drawer")

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        self.polygons = []
        self.current_polygon = []

        # Bind mouse events
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        # Add buttons
        self.save_button = tk.Button(self.master, text="Save as JSON", command=self.save_as_json)
        self.save_button.pack()

        self.ax.set_title("Click to draw a polygon (snapped to grid), close the polygon by clicking the first point")
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.grid(True)

    def onclick(self, event):
        if event.inaxes != self.ax:
            return

        # Snap to grid by rounding to nearest integer
        snapped_x = round(event.xdata)
        snapped_y = round(event.ydata)

        if len(self.current_polygon) > 0 and np.isclose([snapped_x, snapped_y], self.current_polygon[0]).all():
            # Close polygon by connecting to the first point
            polygon = np.array(self.current_polygon)
            self.polygons.append(polygon)
            self.ax.plot(polygon[:, 0], polygon[:, 1], marker='o', linestyle='-')
            self.ax.fill(polygon[:, 0], polygon[:, 1], alpha=0.3)
            self.current_polygon = []
        else:
            # Add point to current polygon
            self.current_polygon.append([snapped_x, snapped_y])
            self.ax.plot(snapped_x, snapped_y, marker='o', color='r')

        self.fig.canvas.draw()

    def save_as_json(self):
        if not self.polygons:
            return

        # Prepare data to save
        polygons_data = [{"points": polygon.tolist()} for polygon in self.polygons]

        # Ask for file path
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(polygons_data, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = PolygonDrawer(root)
    root.mainloop()