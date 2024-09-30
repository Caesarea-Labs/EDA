# import moderngl_window as mglw
# import moderngl
# import numpy as np
# from typing import Tuple, Any, cast
# from numpy.typing import NDArray

# class CubeWindow(mglw.WindowConfig):
#     gl_version: Tuple[int, int] = (3, 3)
#     title: str = "ModernGL Cube"

#     def __init__(self, **kwargs: Any):
#         super().__init__(**kwargs)

#         self.prog: moderngl.Program = self.ctx.program(
#             vertex_shader='''
#                 #version 330

#                 in vec3 in_position;
#                 in vec3 in_color;

#                 out vec3 color;

#                 uniform mat4 model;
#                 uniform mat4 view;
#                 uniform mat4 projection;

#                 void main() {
#                     gl_Position = projection * view * model * vec4(in_position, 1.0);
#                     color = in_color;
#                 }
#             ''',
#             fragment_shader='''
#                 #version 330

#                 in vec3 color;
#                 out vec4 fragColor;

#                 void main() {
#                     fragColor = vec4(color, 1.0);
#                 }
#             '''
#         )

#         # Cube vertices and colors
#         vertices= np.array([
#             # Front face (red)
#             -0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
#              0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
#              0.5,  0.5,  0.5,  1.0, 0.0, 0.0,
#             -0.5,  0.5,  0.5,  1.0, 0.0, 0.0,
#             # Back face (green)
#             -0.5, -0.5, -0.5,  0.0, 1.0, 0.0,
#              0.5, -0.5, -0.5,  0.0, 1.0, 0.0,
#              0.5,  0.5, -0.5,  0.0, 1.0, 0.0,
#             -0.5,  0.5, -0.5,  0.0, 1.0, 0.0,
#             # Top face (blue)
#             -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
#              0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
#              0.5,  0.5, -0.5,  0.0, 0.0, 1.0,
#             -0.5,  0.5, -0.5,  0.0, 0.0, 1.0,
#             # Bottom face (yellow)
#             -0.5, -0.5,  0.5,  1.0, 1.0, 0.0,
#              0.5, -0.5,  0.5,  1.0, 1.0, 0.0,
#              0.5, -0.5, -0.5,  1.0, 1.0, 0.0,
#             -0.5, -0.5, -0.5,  1.0, 1.0, 0.0,
#             # Right face (magenta)
#              0.5, -0.5,  0.5,  1.0, 0.0, 1.0,
#              0.5, -0.5, -0.5,  1.0, 0.0, 1.0,
#              0.5,  0.5, -0.5,  1.0, 0.0, 1.0,
#              0.5,  0.5,  0.5,  1.0, 0.0, 1.0,
#             # Left face (cyan)
#             -0.5, -0.5,  0.5,  0.0, 1.0, 1.0,
#             -0.5, -0.5, -0.5,  0.0, 1.0, 1.0,
#             -0.5,  0.5, -0.5,  0.0, 1.0, 1.0,
#             -0.5,  0.5,  0.5,  0.0, 1.0, 1.0,
#         ], dtype='f4')

#         indices= np.array([
#             0,  1,  2,  2,  3,  0,  # Front face
#             4,  5,  6,  6,  7,  4,  # Back face
#             8,  9, 10, 10, 11,  8,  # Top face
#             12, 13, 14, 14, 15, 12,  # Bottom face
#             16, 17, 18, 18, 19, 16,  # Right face
#             20, 21, 22, 22, 23, 20,  # Left face
#         ], dtype='u4')

#         self.vbo: moderngl.Buffer = self.ctx.buffer(vertices)
#         self.ibo: moderngl.Buffer = self.ctx.buffer(indices)

#         self.vao: moderngl.VertexArray = self.ctx.vertex_array(
#             self.prog,
#             [
#                 (self.vbo, '3f 3f', 'in_position', 'in_color'),
#             ],
#             self.ibo
#         )

#         self.model: moderngl.Uniform = cast(moderngl.Uniform, self.prog['model'])
#         self.view: moderngl.Uniform = cast(moderngl.Uniform,self.prog['view'])
#         self.projection: moderngl.Uniform = cast(moderngl.Uniform,self.prog['projection'])
        
#     def render(self, time: float, frame_time: float) -> None:
#         self.ctx.clear(0.9, 0.9, 0.9)
#         self.ctx.enable(moderngl.DEPTH_TEST)

#         proj = np.eye(4, dtype='f4')
#         proj[3, 3] = 0.0
#         proj[3, 2] = -1 / 5
#         self.projection.write(proj.astype('f4').tobytes())

#         view = np.eye(4, dtype='f4')
#         view[3, 2] = -3
#         self.view.write(view.astype('f4').tobytes())

#         model = self.create_rotation_matrix(time)
#         self.model.write(model.astype('f4').tobytes())

#         self.vao.render()

#     @staticmethod
#     def create_rotation_matrix(angle: float) -> NDArray[np.float64]:
#         cos = np.cos(angle)
#         sin = np.sin(angle)
#         rx = np.array([
#             [1, 0, 0, 0],
#             [0, cos, -sin, 0],
#             [0, sin, cos, 0],
#             [0, 0, 0, 1]
#         ], dtype='f4')
#         ry = np.array([
#             [cos, 0, sin, 0],
#             [0, 1, 0, 0],
#             [-sin, 0, cos, 0],
#             [0, 0, 0, 1]
#         ], dtype='f4')
#         rz = np.array([
#             [cos, -sin, 0, 0],
#             [sin, cos, 0, 0],
#             [0, 0, 1, 0],
#             [0, 0, 0, 1]
#         ], dtype='f4')
#         return rx @ ry @ rz

# if __name__ == '__main__':
#     mglw.run_window_config(CubeWindow)