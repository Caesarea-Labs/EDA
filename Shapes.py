from dataclasses import dataclass

from Layout import Point2D, MetalPolygon, Point2DFloat


@dataclass
class Shape2D:
    """Represents a 2D shape with a name. Has many utility methods for transforming the shape"""
    vertices: list[Point2D]
    shape_type: str
    center: Point2DFloat
    name: str

    def named(self, name: str) -> 'Shape2D':
        return Shape2D(shape_type=self.shape_type, vertices=self.vertices, center=self.center, name=name)

    def with_vertices(self, vertices: list[Point2D]) -> 'Shape2D':
        return Shape2D(shape_type=self.shape_type, vertices=vertices, center=self.center, name=self.name)

    def with_vertices_and_center(self, vertices: list[Point2D], new_center: Point2DFloat) -> 'Shape2D':
        return Shape2D(shape_type=self.shape_type, vertices=vertices, center=new_center, name=self.name)

    def metal(self, layer: int, signal_index: int = 0) -> MetalPolygon:
        return MetalPolygon(vertices=self.vertices, layer=layer, signal_index=signal_index, name=self.name)

    def rotate(self, angle: int) -> 'Shape2D':
        """Rotates the shape by multiples of 90 degrees."""

        if angle == 0 or angle == 360:
            return self
        else:
            cx = self.center.x
            cy = self.center.y

            # Step 2: Apply the appropriate rotation based on the angle
            if angle == 90:
                return self.with_vertices([Point2D(cx - (y - cy), cy + (x - cx)) for x, y in self.vertices])
            elif angle == 180:
                return self.with_vertices([Point2D(2 * cx - x, 2 * cy - y) for x, y in self.vertices])
            elif angle == 270:
                return self.with_vertices([Point2D(cx + (y - cy), cy - (x - cx)) for x, y in self.vertices])
            else:
                raise ValueError("Angle must be 90, 180, or 270 degrees")
        pass

    def translate(self, translate_x: int, translate_y: int) -> 'Shape2D':
        """Moves all vertices by the given x and y translation values."""
        return self.with_vertices_and_center(
            [Point2D(x + translate_x, y + translate_y) for (x, y) in self.vertices],
            new_center=Point2DFloat(self.center.x + translate_x, self.center.y + translate_y)
        )

    def mirror_horizontal(self):
        """Mirrors the shape along the X axis"""
        mirrored = [Point2D(x, 2 * self.center.y - y) for x, y in self.vertices]

        return self.with_vertices(mirrored)

    def mirror_vertical(self):
        """Mirrors the shape along the X axis"""
        mirrored = [Point2D(2 * self.center.x - x, y) for x, y in self.vertices]

        return self.with_vertices(mirrored)


def build_shape(type_name: str, center: Point2DFloat, pairs: list[(int, int)], name: str) -> Shape2D:
    return Shape2D(shape_type=type_name, vertices=[Point2D(x, y) for x, y in pairs], center=center, name=name)


def s_shape(x_spacing: int, y_spacing: int, x_thickness: int, y_thickness: int, name: str = "Shape") -> Shape2D:
    return build_shape(
        "S",
        center=Point2DFloat((x_thickness + x_spacing) / 2, (y_thickness + y_spacing) / 2),
        pairs=[
            (0, 0),
            (0, y_thickness),
            (x_thickness + x_spacing, y_thickness),
            (x_thickness + x_spacing, y_thickness + y_spacing),
            (0, y_thickness + y_spacing),
            (0, 3 * y_thickness + y_spacing * 2),
            (2 * x_thickness + x_spacing, 3 * y_thickness + y_spacing * 2),
            (2 * x_thickness + x_spacing, 2 * y_thickness + y_spacing * 2),
            (x_thickness, 2 * y_thickness + y_spacing * 2),
            (x_thickness, 2 * y_thickness + y_spacing),
            (2 * x_thickness + x_spacing, 2 * y_thickness + y_spacing),
            (2 * x_thickness + x_spacing, 0)
        ],
        name=name
    )


def lamed_shape(x_spacing: int, y_spacing: int, x_thickness: int, y_thickness: int, name: str = "Shape") -> Shape2D:
    return build_shape(
        "lamed",
        center=Point2DFloat((x_thickness + x_spacing) / 2, (y_thickness + y_spacing) / 2),
        pairs=[
            (0, 0),
            (x_thickness, 0),
            (x_thickness, y_spacing),
            (x_thickness * 2 + x_spacing, y_spacing),
            (x_thickness * 2 + x_spacing, y_spacing * 2 + y_thickness),
            (x_thickness + x_spacing, y_spacing * 2 + y_thickness),
            (x_thickness + x_spacing, y_spacing + y_thickness),
            (0, y_spacing + y_thickness)
        ],
        name=name
    )


def L_shape(x_spacing: int, y_spacing: int, x_thickness: int, y_thickness, name: str = "Shape") -> Shape2D:
    return build_shape(
        "L",
        Point2DFloat((x_thickness + x_spacing) / 2, (y_thickness + y_spacing) / 2),
        [
            (0, 0),
            (x_spacing + x_thickness, 0),
            (x_spacing + x_thickness, y_thickness),
            (x_thickness, y_thickness),
            (x_thickness, y_spacing + y_thickness),
            (0, y_spacing + y_thickness)
        ],
        name=name
    )


def rect_shape(width: int, height: int, name: str = "Shape") -> Shape2D:
    return build_shape(
        type_name="rect",
        center=Point2DFloat(width / 2, height / 2),
        pairs=[
            (0, 0),
            (width, 0),
            (width, height),
            (0, height)
        ],
        name=name
    )

# rectangle_shape = buildShape(
#     "rectangle",
#     [
#         (0, 0),
#         (1, 0),
#         (1, 2),
#         (0, 2)
#     ]
# )
