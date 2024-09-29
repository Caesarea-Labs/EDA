from dataclasses import dataclass
from typing import Any, cast
import numpy as np
from geometry.geometry import Point2D
from layout import Layout
from polygon_triangulizer import AnnotatedMesh, ExtrudedPolygon, polygon_to_mesh
import pyvista as pv

from utils import none_check

fill_colors = ['cyan', 'lightgreen', 'lightblue', 'orange', 'yellow',
               'pink', 'lightcoral', 'lightgray', 'lavender', 'beige']


def pyvista_plot_layout(layout: Layout, show_text: bool):
    """
    Will draw the layout in 3D.
    If show_text is true, every metal and via will have its named displayed. This should be turned off for large layouts. 
    """
    meshes = []

    for metal in layout.metals:
        polygon = ExtrudedPolygon(
            z_base=none_check(metal.layer) - 0.25,
            z_top=none_check(metal.layer) + 0.25,
            color=fill_colors[none_check(metal.signal_index) % len(fill_colors)],
            # edge_color=edge_colors[metal.signal_index % len(edge_colors)],
            vertices=metal.polygon,
            alpha=0.5,
            name=metal.name,
            group_name=str(metal.signal_index)
        )
        meshes.append(polygon_to_mesh(polygon))

    for via in layout.vias:
        polygon = ExtrudedPolygon(
            z_base=none_check(via.layer) if not via.mark else 0,
            z_top=none_check(via.layer) + 1,
            color="red" if via.mark else "black",
            vertices=via.rect.as_polygon(),
            alpha=0.3,
            name=via.name,
            group_name="vias"
        )
        meshes.append(polygon_to_mesh(polygon))

    # Convert polygons to meshes
    pyvista_plot_meshes(meshes, show_text)


@dataclass
class SetVisibilityCallback:
    actors: list[pv.Actor]

    def __call__(self, visible: bool):
        for actor in self.actors:
            actor.SetVisibility(visible)


MeshDict = dict[str, tuple[str, list[pv.Actor]]]


def pyvista_plot_meshes(meshes: list[AnnotatedMesh], show_text: bool):
    # Plot the mesh
    plotter = pv.Plotter()

    # First element of tuple is the color of the group, second element is meshes in the group.
    meshes_by_group: MeshDict = {}

    for mesh in meshes:
        add_mesh_to_plotter(plotter, mesh, meshes_by_group, show_text)

    for i, (group, (color, mesh_actors)) in enumerate(meshes_by_group.items()):
        checkbox_actor = plotter.add_checkbox_button_widget(SetVisibilityCallback(mesh_actors), value=True,
                                           position=(5, 12 + i * 35), size=30,
                                           border_size=1,
                                           color_on=color,
                                           color_off='grey',
                                           background_color='grey')
        checkbox_actor.
        # checkbox_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        

        text_actor = plotter.add_text(group, position=(1,1), viewport=True)  # type: ignore

        # def update_text_position(caller: Any = None, event: Any = None):
        #     window_size = plotter.window_size  # Get the current window size
        #     size = [0, 0]
        #     text_actor.GetSize(plotter.renderer, size)  # Get the size of the text
        #     # Set the text position to be 5 pixels left and down from the top-right corner
        #     text_actor.SetDisplayPosition(
        #         round(window_size[0] - size[0] - 5),  # X position
        #         round(window_size[1] - size[1] - 5 - i * 35)   # Y position
        #     )
        # text_prop = text_actor.GetTextProperty()
        # text_prop.SetJustificationToRight()
        # text_prop.SetVerticalJustificationToTop()

        # text_actor.SetPosition2(0, 0)  # Reset any scaling
        # text_actor.SetPosition(-40.0, -12 - i * 35)

        # plotter.iren.add_observer('RenderEvent', update_text_position)

    # The text you want to display
    # text = 'Your Text Here'

    # # Add the text to the plotter with viewport coordinates
    # text_actor = plotter.add_text(
    #     text,
    #     position=(0.1, 0.9),       # Position at the top-right corner
    # )

    # text_actor.GetPositionCoordinate()
    # text_actor.GetPositionCoordinate().SetValue(0.9,0.1)

    # Access the text property to adjust justification
    # text_prop = text_actor.GetTextProperty()
    # text_prop.SetJustificationToRight()
    # text_prop.SetVerticalJustificationToTop()

    # # Offset the text by 5 pixels left and down
    # text_actor.SetPosition2(0, 0)  # Reset any scaling
    # text_actor.AddPosition(-5, -5)  # Offset by -5 pixels in x and y

    # Create the figure and show it
    cast(pv.Camera, plotter.camera).SetViewUp(0,-1,0)
    plotter.show()


def add_mesh_to_plotter(plotter: pv.Plotter, mesh: AnnotatedMesh, meshes: MeshDict, draw_text: bool):
    polygon_actor = cast(pv.Actor, plotter.add_mesh(mesh_to_pyvista_polydata(mesh), show_edges=False, color=mesh.color, opacity=mesh.alpha))

    # Add meshes to mesh group so they can be toggled off
    if mesh.group_name in meshes:
        meshes[mesh.group_name][1].append(polygon_actor)
    else:
        # Use the color of the first mesh as the group color
        meshes[mesh.group_name] = (mesh.color, [polygon_actor])

    if draw_text:
        # Normal = 1,0,0 to make it mostly face the camera
        text_actor = plotter.add_mesh(pv.Text3D(mesh.name, center=mesh.center().to_tuple(), height=0.3, normal=(1, 0, 0)))
        # Make it so turning off the polygon will turn off the text too
        meshes[mesh.group_name][1].append(text_actor)


def mesh_to_pyvista_polydata(mesh: AnnotatedMesh) -> pv.PolyData:
    """
    Converts an AnnotatedMesh into a PyVista PolyData object.

    Args:
    mesh: AnnotatedMesh object containing vertices, triangle indices, color, alpha, name, and group_name.

    Returns:
    A PyVista PolyData object representing the mesh.
    """
    # Extract vertices
    # This will cause a warning right now because we don't pass proper float32's
    points = np.array([[v.x, v.y, v.z] for v in mesh.vertices])

    # Extract triangle faces and convert them to PyVista format
    triangles = np.array([[3, t.a_index, t.b_index, t.c_index] for t in mesh.triangles])

    # Create PolyData object
    polydata = pv.PolyData(points, triangles)
    return polydata


if __name__ == "__main__":
    polygon_1 = ExtrudedPolygon(
        z_base=0, z_top=1,
        vertices=[
            Point2D(0, 0),  # Bottom-left corner
            Point2D(2, 0),  # Bottom-right corner
            Point2D(2, 1),  # Middle-right corner
            Point2D(3, 1),  # Middle-right overhang
            Point2D(3, 2),  # Top-right overhang
            Point2D(1, 2),  # Top-left corner of overhang
            Point2D(1, 1),  # Middle-left corner
            Point2D(0, 1)   # Back to bottom-left corner
        ],
        color="blue", alpha=0.3, name="test1", group_name="1"
    )

    polygon_2 = ExtrudedPolygon(
        z_base=10, z_top=11,
        vertices=[
            Point2D(0, 0),  # Bottom-left corner
            Point2D(2, 0),  # Bottom-right corner
            Point2D(2, 1),  # Middle-right corner
            Point2D(3, 1),  # Middle-right overhang
            Point2D(3, 2),  # Top-right overhang
            Point2D(1, 2),  # Top-left corner of overhang
            Point2D(1, 1),  # Middle-left corner
            Point2D(0, 1)   # Back to bottom-left corner
        ],
        color="blue", alpha=0.3, name="test2", group_name="2"
    )

    pyvista_plot_meshes([
        polygon_to_mesh(polygon_1), polygon_to_mesh(polygon_2)
    ], show_text=True)
