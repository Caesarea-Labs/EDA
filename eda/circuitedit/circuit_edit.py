from __future__ import annotations
from dataclasses import dataclass

from eda import layout
from eda.geometry.geometry import Rect2D, Rect3D
from eda.geometry.polygon_triangulizer import AnnotatedMesh, ExtrudedPolygon, polygon_to_mesh
from eda.layout import Layout, Via, via_to_mesh
from eda.ui.plottable import Plottable
from eda.utils import none_check


@dataclass
class EditedLayout(Plottable):
    layout: Layout
    edit: CircuitEdit

    def to_meshes(self) -> list[AnnotatedMesh]:
        meshes = []
        for via in self.edit.via_insertions:
            meshes.append(
                via_to_mesh(via, color="red", group_name="Edits")
            )

        meshes.extend(self.layout.to_meshes())
        for cut in self.edit.cuts:
            polygon = ExtrudedPolygon(
                z_base=cut.pos.z - 0.25,
                z_top=cut.pos.z + 0.25,
                color="red",
                vertices=cut.pos.only_2d().as_polygon(),
                alpha=0.3,
                name="Cut",
                group_name="Cuts"
            )
            meshes.append(polygon_to_mesh(polygon))
        return meshes


@dataclass
class CircuitEdit:
    via_insertions: list[Via]
    cuts: list[Cut]


@dataclass
class Cut:
    pos: Rect3D
