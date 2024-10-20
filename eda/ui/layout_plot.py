from dataclasses import dataclass
from typing import Any, TypedDict, cast
import numpy as np
from pyvistaqt import QtInteractor

from eda.ui.plottable import Plottable
from ..geometry.geometry import Point2D
from ..layout import Layout
from ..geometry.polygon_triangulizer import AnnotatedMesh, ExtrudedPolygon, polygon_to_mesh
import pyvista as pv
import vtk

from ..utils import none_check


MeshGroup = TypedDict("MeshGroup", color=str, actor=pv.Actor)
MeshDict = dict[str, MeshGroup]


@dataclass
class LayoutPlotBindings:
    mesh_groups: MeshDict


def plot_layout_standalone(layout: Plottable, show_text: bool = False):
    plotter = pv.Plotter()
    plot_meshes(layout.to_meshes(), show_text, plotter)
    plotter.show()


# def add_layout_elements_to_plot(layout: Layout, show_text: bool, plotter: pv.Plotter) -> LayoutPlotBindings:
    
#     """
#     Will draw the layout in 3D.
#     If show_text is true, every metal and via will have its named displayed. This should be turned off for large layouts. 
#     """
#     meshes = []

#     for via in layout.vias:
#         polygon = ExtrudedPolygon(
#             z_base=none_check(via.bottom_layer),
#             z_top=none_check(via.top_layer, f"Missing top_layer value for via (bottom_layer is specified: {via.bottom_layer})"),
#             color="red" if via.mark else "black",
#             vertices=via.rect.as_polygon(),
#             alpha=0.3,
#             name=via.name,
#             group_name="edit" if via.mark else "vias"
#         )
#         meshes.append(polygon_to_mesh(polygon))

#     for metal in layout.metals:
#         polygon = ExtrudedPolygon(
#             z_base=none_check(metal.layer) - 0.25,
#             z_top=none_check(metal.layer) + 0.25,
#             color=fill_colors[none_check(metal.signal_index) % len(fill_colors)],
#             # edge_color=edge_colors[metal.signal_index % len(edge_colors)],
#             vertices=metal.polygon,
#             alpha=0.5,
#             name=metal.name,
#             group_name=str(metal.signal_index)
#         )
#         meshes.append(polygon_to_mesh(polygon))

    

#     # Convert polygons to meshes
#     return plot_meshes(meshes, show_text, plotter)


# @dataclass
# class SetVisibilityCallback:
#     actors: list[pv.Actor]

#     def __call__(self, visible: bool):
#         for actor in self.actors:
#             actor.SetVisibility(visible)


def plot_meshes(meshes: list[AnnotatedMesh], show_text: bool, plotter: pv.BasePlotter) -> LayoutPlotBindings:
    # Plot the mesh
    # plotter = pv.Plotter()

    # First element of tuple is the color of the group, second element is meshes in the group.
    meshes_by_group: dict[str, list[AnnotatedMesh]] = {}

    for mesh in meshes:
        if mesh.group_name in meshes_by_group:
            meshes_by_group[mesh.group_name].append(mesh)
        else:
            # Use the color of the first mesh as the group color
            meshes_by_group[mesh.group_name] = [mesh]

    group_bindings: MeshDict = {}

    for group_name, group_meshes in meshes_by_group.items():
        # Group the meshes in multiblocks for performance reasons
        multiblock = pv.MultiBlock()
        color = group_meshes[0].color
        opacity = group_meshes[0].alpha
        for mesh in group_meshes:
            # plotter.add_mesh(mesh_to_pyvista_polydata(mesh), show_edges=False, color=color, opacity=opacity)
            multiblock.append(mesh_to_pyvista_polydata(mesh))
            if show_text:
                # Normal = 1,0,0 to make it mostly face the camera
                # stfu Text3D is an acceptable input here
                multiblock.append(pv.Text3D(mesh.name, center=mesh.center().to_tuple(), height=0.3, normal=(1, 0, 0)))  # type: ignore

        # Use the color and opacity of the first item in the group (Can consider making those not a per-mesh property)
        # render=false can improve performance significantly when drawing with QT
        binding: pv.Actor = plotter.add_mesh(multiblock, show_edges=False, color=color, opacity=opacity, render=False)
        # Store a reference to an actor that may hide/show the multiblock
        group_bindings[group_name] = {'actor': binding, 'color': color}

    # for mesh in meshes:
    # plotter.add_mesh(mesh_to_pyvista_polydata(mesh)
    # plotter.show()

    # QtInteractor()

    return LayoutPlotBindings(group_bindings)

    # for i, (group, (color, mesh_actors)) in enumerate(meshes_by_group.items()):
    #     checkbox_actor = plotter.add_checkbox_button_widget(SetVisibilityCallback(mesh_actors), value=True,
    #                                        position=(5, 12 + i * 35), size=30,
    #                                        border_size=1,
    #                                        color_on=color,
    #                                        color_off='grey',
    #                                        background_color='grey')
    #     checkbox_actor.
    #     # checkbox_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()

    #     text_actor = plotter.add_text(group, position=(1,1), viewport=True)  # type: ignore

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
    # cast(pv.Camera, plotter.camera).SetViewUp(0,-1,0)
    # plotter.show()


# def add_mesh_to_multiblock(block: pv.Plotter, mesh: AnnotatedMesh, meshes: MeshDict, draw_text: bool):
#     polygon_actor = cast(pv.Actor, plotter.add_mesh(mesh_to_pyvista_polydata(mesh), show_edges=False, color=mesh.color, opacity=mesh.alpha))

#     # # Add meshes to mesh group so they can be toggled off
#     # if mesh.group_name in meshes:
#     #     meshes[mesh.group_name][1].append(polygon_actor)
#     # else:
#     #     # Use the color of the first mesh as the group color
#     #     meshes[mesh.group_name] = (mesh.color, [polygon_actor])

#     # if draw_text:
#         # Normal = 1,0,0 to make it mostly face the camera
#     plotter.add_mesh(pv.Text3D(mesh.name, center=mesh.center().to_tuple(), height=0.3, normal=(1, 0, 0)))
#         # Make it so turning off the polygon will turn off the text too
#         # meshes[mesh.group_name][1].append(text_actor)


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
