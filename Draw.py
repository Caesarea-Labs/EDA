from dataclasses import dataclass

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from numpy.ma.core import shape

from Layout import MetalPolygon, Point2D, Layout, Via, Rect2D

fill_colors = ['cyan', 'lightgreen', 'lightblue', 'orange', 'yellow',
               'pink', 'lightcoral', 'lightgray', 'lavender', 'beige']

edge_colors = ['red', 'blue', 'green', 'purple', 'black',
               'brown', 'darkblue', 'darkgreen', 'darkred', 'darkorange']


@dataclass
class Polygon3D:
    """
    Generic representation of any kind of polygon that spans across multiple z values
    """
    z_base: float
    z_top: float
    vertices: list[Point2D]
    fill_color: str
    edge_color: str
    alpha: float
    name: str


def plot_layout(layout: Layout, size: int = 10, height: int = 10):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_zlim(0, height)
    ax.set_ylim(0, size)
    ax.set_xlim(0, size)

    def draw_shape(shape: Polygon3D):
        x_coords = [point.x for point in shape.vertices]  # Get the x coordinates
        y_coords = [point.y for point in shape.vertices]  # Get the y coordinates

        # Define the base and the top of the shape
        base = [(x, y, shape.z_base) for x, y in zip(x_coords, y_coords)]  # Base at z_base
        top = [(x, y, shape.z_top) for x, y in zip(x_coords, y_coords)]  # Top at z_top

        # Create the sides of the 3D shape
        sides = [[base[i], base[(i + 1) % len(base)], top[(i + 1) % len(top)], top[i]] for i in range(len(base))]

        # Plot the base and the top
        ax.add_collection3d(
            Poly3DCollection([base], facecolors=shape.fill_color, linewidths=1, edgecolors=shape.edge_color,
                             alpha=shape.alpha))
        ax.add_collection3d(
            Poly3DCollection([top], facecolors=shape.fill_color, linewidths=1, edgecolors=shape.edge_color,
                             alpha=shape.alpha))

        # Plot the sides
        ax.add_collection3d(
            Poly3DCollection(sides, facecolors=shape.fill_color, linewidths=1, edgecolors=shape.edge_color,
                             alpha=shape.alpha))

        # Calculate the center of the polygon
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        center_z = (shape.z_base + shape.z_top) / 2

        # Add the name text at the center of the polygon
        ax.text3D(center_x, center_y, center_z, shape.name,
                  horizontalalignment='center', verticalalignment='center')

    for metal in layout.metals:
        polygon = Polygon3D(
            z_base=metal.layer - 0.25,
            z_top=metal.layer + 0.25,
            fill_color=fill_colors[metal.signal_index % len(fill_colors)],
            edge_color=edge_colors[metal.signal_index % len(edge_colors)],
            vertices=metal.vertices,
            alpha=0.5,
            name=metal.name
        )
        draw_shape(polygon)

    for via in layout.vias:
        polygon = Polygon3D(
            z_base=via.bottomLayer,
            z_top=via.topLayer,
            fill_color="black",
            edge_color="white",
            vertices=via.rect.vertices(),
            alpha=0.3,
            name=via.name
        )
        draw_shape(polygon)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Shape Layout')
    plt.show()


if __name__ == '__main__':
    triangle = MetalPolygon(vertices=[Point2D(0, 0), Point2D(2, 0), Point2D(1, 2)], layer=2)
    square = MetalPolygon(vertices=[Point2D(3, 3), Point2D(3, 7), Point2D(7, 7), Point2D(7, 3)], layer=0)
    s_shape = MetalPolygon(
        vertices=[
            Point2D(2, 2),
            Point2D(2, 4),
            Point2D(0, 4),
            Point2D(0, 7),
            Point2D(1, 7),
            Point2D(1, 5),
            Point2D(3, 5),
            Point2D(3, 2)
        ], layer=1
    )
    l_shape = MetalPolygon(
        vertices=[
            Point2D(1, 3),
            Point2D(1, 4),
            Point2D(4, 4),
            Point2D(4, 7),
            Point2D(5, 7),
            Point2D(5, 3)
        ], layer=3
    )

    connection = Via(
        bottomLayer=1,
        topLayer=3,
        rect=Rect2D(x_start=2, x_end=3, y_start=3, y_end=4)
    )

    layout = Layout([triangle, square, s_shape, l_shape], [connection])
    plot_layout(layout)
