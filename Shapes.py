from dataclasses import dataclass

from Layout import Point2D, MetalPolygon


@dataclass
class Shape2D:
    """Represents a 2D shape with a name. Has many utility methods for transforming the shape"""
    vertices: list[Point2D]
    name: str

    def layer(self, layer: int) -> MetalPolygon:
        return MetalPolygon(vertices=self.vertices, layer=layer)

    # def thickness(self, thickness: int) -> 'Shape2D':
    #     """Makes the shape as wide as the given thickness"""
    #     pass
    #     # TODO

    def rotate(self, right_angle_rotations: int) -> 'Shape2D':
        """Rotates the shape by 90 degrees, the amount of times specified by right_angle_rotations.
         So right_angle_rotations should be 1 for 90 degrees, 2 for 180 degrees, 3 for 270 degrees."""
        pass
        # TODO

    def translate(self, translate_x: int, translate_y: int) -> 'Shape2D':
        """Moves all vertices by the given x and y translation values."""
        pass
        # TODO


def buildShape(name: str, pairs: list[(int, int)]) -> Shape2D:
    return Shape2D(name=name, vertices=[Point2D(x, y) for x, y in pairs])

def s_shape(height: int, width: int, thickness: int) -> Shape2D:
    # TODO
    pass

def lamed_shape(height: int, width: int, thickness: int) -> Shape2D:
    # TODO
    pass

def L_shape(height: int, width: int, thickness: int) -> Shape2D:
    # TODO
    pass

def rect_shape(height: int, width: int) -> Shape2D:
    # TODO
    pass

s_shape = buildShape(
    "S",
    [
        (0, 0),
        (0, 1),
        (2, 1),
        (2, 2),
        (0, 2),
        (0, 5),
        (3, 5),
        (3, 4),
        (1, 4),
        (1, 3),
        (3, 3),
        (3, 0)
    ]
)

L_shape = buildShape(
    "L",
    [
        (0, 0),
        (3, 0),
        (3, 1),
        (1, 1),
        (1, 3),
        (0, 3)
    ]
)

lamed_shape = buildShape(
    "lamed",
    [
        (0, 0),
        (1, 0),
        (1, 2),
        (3, 2),
        (3, 5),
        (2, 5),
        (2, 3),
        (0, 3)
    ]
)

rectangle_shape = buildShape(
    "rectangle",
    [
        (0, 0),
        (1,0),
        (1,2),
        (0,2)
    ]
)