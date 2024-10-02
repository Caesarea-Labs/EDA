import pyvista as pv
import vtk

class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("MouseMoveEvent", self.mouseMoveEvent)
        
        self.TextActor = vtk.vtkTextActor()
        self.TextActor.SetInput("(x, y, z)")
        self.TextActor.GetTextProperty().SetFontSize(12)
        self.TextActor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
        
    def mouseMoveEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()
        
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)
        
        # Pick from this location.
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        
        worldPosition = picker.GetPickPosition()
        
        self.TextActor.SetInput(f"({worldPosition[0]:.2f}, {worldPosition[1]:.2f}, {worldPosition[2]:.2f})")
        
        self.GetInteractor().GetRenderWindow().Render()
        
        # Call parent's mouseMoveEvent
        return vtk.vtkInteractorStyleTrackballCamera.mouseMoveEvent(self, obj, event)

# Create a PyVista plotter
plotter = pv.Plotter()

# Create a sphere mesh
sphere = pv.Sphere(radius=1, center=(0, 0, 0))

# Add the sphere to the plotter
plotter.add_mesh(sphere, color="tan", show_edges=True)

# Get the underlying VTK render window and interactor
render_window = plotter.ren_win
interactor = plotter.iren.interactor

# Set up the custom interactor style
style = MouseInteractorStyle()
style.SetDefaultRenderer(plotter.renderer)
interactor.SetInteractorStyle(style)

# Add the text actor to the renderer
plotter.add_actor(style.TextActor)

# Set up a callback to update the camera position
def update_camera(plotter):
    plotter.camera_position = plotter.get_default_cam_pos()
    plotter.render()

# Set up a callback to update the camera position
@plotter.event_callback('MouseMoveEvent')
def update_text(vtk_obj, event):
    style.mouseMoveEvent(vtk_obj, event)

# Show the plotter
plotter.show()