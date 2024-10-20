from typing import Protocol

from eda.geometry.polygon_triangulizer import AnnotatedMesh, polygon_to_mesh


class Plottable(Protocol):
    def to_meshes(self) -> list[AnnotatedMesh]:
        ...
    