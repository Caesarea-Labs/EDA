from dataclasses import dataclass

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

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


def plot_layout(layout: Layout):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_zlim(0, 10)
    ax.set_ylim(0,10)
    ax.set_xlim(0,10)

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
            Poly3DCollection([base], facecolors=shape.fill_color, linewidths=1, edgecolors=shape.edge_color, alpha=0.5))
        ax.add_collection3d(
            Poly3DCollection([top], facecolors=shape.fill_color, linewidths=1, edgecolors=shape.edge_color, alpha=0.5))

        # Plot the sides
        ax.add_collection3d(
            Poly3DCollection(sides, facecolors=shape.fill_color, linewidths=1, edgecolors=shape.edge_color, alpha=0.5))

    for metal in layout.metals:
        polygon = Polygon3D(
            z_base=metal.layer - 0.25,
            z_top=metal.layer + 0.25,
            fill_color=fill_colors[metal.layer % len(fill_colors)],
            edge_color=edge_colors[metal.layer % len(edge_colors)],
            vertices=metal.vertices
        )
        draw_shape(polygon)

    for via in layout.vias:
        polygon = Polygon3D(
            z_base=via.bottomLayer,
            z_top=via.topLayer,
            fill_color="black",
            edge_color="white",
            vertices=via.rect.vertices()
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


