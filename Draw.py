import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from Layout import Shape2D, Point2D, Layout

fill_colors = ['cyan', 'lightgreen', 'lightblue', 'orange', 'yellow',
               'pink', 'lightcoral', 'lightgray', 'lavender', 'beige']

edge_colors = ['red', 'blue', 'green', 'purple', 'black',
               'brown', 'darkblue', 'darkgreen', 'darkred', 'darkorange']


def plot_layout(layout: Layout):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_zlim(0,6)

    for layer_idx, layer in enumerate(layout.layers):
        z_base = layer_idx  # Base of the layer at z = layer_idx
        z_top = layer_idx + 0.5  # Top of the layer at z = layer_idx + 1

        for shape in layer:
            x_coords = [point.x for point in shape.edges]  # Get the x coordinates
            y_coords = [point.y for point in shape.edges]  # Get the y coordinates

            # Define the base and the top of the shape
            base = [(x, y, z_base) for x, y in zip(x_coords, y_coords)]  # Base at z_base
            top = [(x, y, z_top) for x, y in zip(x_coords, y_coords)]  # Top at z_top

            # Create the sides of the 3D shape
            sides = [[base[i], base[(i + 1) % len(base)], top[(i + 1) % len(top)], top[i]] for i in range(len(base))]

            fill_color = fill_colors[layer_idx % len(fill_colors)]
            edge_color = edge_colors[layer_idx % len(edge_colors)]

            # Plot the base and the top
            ax.add_collection3d(Poly3DCollection([base], facecolors=fill_color, linewidths=1, edgecolors=edge_color, alpha=0.5))
            ax.add_collection3d(Poly3DCollection([top], facecolors=fill_color, linewidths=1, edgecolors=edge_color, alpha=0.5))

            # Plot the sides
            ax.add_collection3d(Poly3DCollection(sides, facecolors=fill_color, linewidths=1, edgecolors=edge_color, alpha=0.5))

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Shape Layout')
    plt.show()

triangle = Shape2D(edges=[Point2D(0, 0), Point2D(2, 0), Point2D(1, 2)])
square = Shape2D(edges=[Point2D(3, 3), Point2D(3, 7), Point2D(7, 7), Point2D(7, 3)])
s_shape = Shape2D(
    edges=[
        Point2D(2,2),
        Point2D(2,4),
        Point2D(0,4),
        Point2D(0,7),
        Point2D(1,7),
        Point2D(1,5),
        Point2D(3,5),
        Point2D(3,2)
    ]
)
l_shape = Shape2D(
    edges=[
        Point2D(1,3),
        Point2D(1,4),
        Point2D(4,4),
        Point2D(4,7),
        Point2D(5,7),
        Point2D(5,3)
    ]
)

layout = Layout([[triangle], [square], [s_shape], [l_shape]])
plot_layout(layout)