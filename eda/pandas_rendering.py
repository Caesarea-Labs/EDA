from panda3d.core import Geom, GeomNode, GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, GeomTristrips, NodePath
from direct.showbase.ShowBase import ShowBase

class ExtrudePolygon(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Define base polygon points (2D square for simplicity)
        base_polygon: list[tuple[float, float]] = [
            (-1, -1),  # Bottom-left
            (1, -1),   # Bottom-right
            (1, 1),    # Top-right
            (-1, 1)    # Top-left
        ]
        height = 2  # Height of extrusion

        # Create the geometry node
        geom_node = self.extrude_polygon(base_polygon, height)
        
        # Attach the geometry to the scene graph
        node_path = NodePath(geom_node)
        node_path.reparent_to(self.render)

        # Add basic lighting and camera settings for visualization
        self.cam.set_pos(0, -10, 5)
        self.cam.look_at(0, 0, 1)
    
    def extrude_polygon(self, polygon: list[tuple[float, float]], height: float):
        # Prepare to build the geometry
        format = GeomVertexFormat.get_v3()
        vdata = GeomVertexData("extruded_polygon", format, Geom.UH_static)
        vertex_writer = GeomVertexWriter(vdata, "vertex")

        # Prepare containers for vertices
        top_vertices: list[int] = []
        bottom_vertices: list[int] = []

        # Create top and bottom vertices
        for x, y in polygon:
            vertex_writer.add_data3(x, y, height)  # Top vertices
            top_vertices.append(vertex_writer.get_write_row() - 1)

            vertex_writer.add_data3(x, y, 0)  # Bottom vertices
            bottom_vertices.append(vertex_writer.get_write_row() - 1)

        geom = Geom(vdata)

        # Create sides of the extrusion (connecting top and bottom vertices)
        tris = GeomTriangles(Geom.UH_static)
        num_vertices = len(polygon)

        for i in range(num_vertices):
            # Connect each pair of adjacent vertices
            next_i = (i + 1) % num_vertices
            tris.add_vertices(top_vertices[i], top_vertices[next_i], bottom_vertices[i])
            tris.add_vertices(bottom_vertices[i], top_vertices[next_i], bottom_vertices[next_i])

        # Close the top and bottom
        self.create_face(tris, top_vertices)     # Top face
        self.create_face(tris, bottom_vertices[::-1])  # Bottom face (reversed)

        # Add the triangles to the geometry
        geom.add_primitive(tris)

        # Create a GeomNode to attach to the scene graph
        geom_node = GeomNode("extruded_polygon")
        geom_node.add_geom(geom)
        
        return geom_node

    def create_face(self, tris: GeomTriangles, vertices: list[int]):
        # Create the face of a polygon (assumes convex)
        num_vertices = len(vertices)
        for i in range(1, num_vertices - 1):
            tris.add_vertices(vertices[0], vertices[i], vertices[i + 1])

# Run the Panda3D app
app = ExtrudePolygon()
app.run()
