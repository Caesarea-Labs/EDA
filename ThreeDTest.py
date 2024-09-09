import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from dataclasses import dataclass, field
from typing import List


@dataclass
class Point3D:
    x: float
    y: float
    z: float


@dataclass
class Shape3D:
    vertices: List[Point3D] = field(default_factory=list)
    faces: List[List[int]] = field(default_factory=list)  # Faces are defined by indices of vertices


class Layout3D:
    def __init__(self, shapes=None):
        if shapes is None:
            shapes = []
        self.shapes = shapes

    def add_shape(self, shape: Shape3D):
        self.shapes.append(shape)

    def plot_layout(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for shape in self.shapes:
            vertices = [(v.x, v.y, v.z) for v in shape.vertices]  # Convert to tuples of (x, y, z)

            for face in shape.faces:
                # Get the vertices of each face
                face_vertices = [vertices[i] for i in face]
                # Create a 3D polygon for the face
                poly3d = [face_vertices]
                ax.add_collection3d(
                    Poly3DCollection(poly3d, facecolors='cyan', linewidths=1, edgecolors='r', alpha=0.5))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.title('3D Shape Layout')

        plt.show()


# Example Usage
# Cube vertices and faces
cube_vertices = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),
                 Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)]

cube_faces = [[0, 1, 2, 3],  # Bottom face
              [4, 5, 6, 7],  # Top face
              [0, 1, 5, 4],  # Front face
              [2, 3, 7, 6],  # Back face
              [0, 3, 7, 4],  # Left face
              [1, 2, 6, 5]]  # Right face

cube = Shape3D(vertices=cube_vertices, faces=cube_faces)

# Pyramid vertices and faces
pyramid_vertices = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0), Point3D(0.5, 0.5, 1)]
pyramid_faces = [[0, 1, 2, 3],  # Base
                 [0, 1, 4],  # Sides
                 [1, 2, 4],
                 [2, 3, 4],
                 [3, 0, 4]]

pyramid = Shape3D(vertices=pyramid_vertices, faces=pyramid_faces)

layout = Layout3D([cube, pyramid])
layout.plot_layout()