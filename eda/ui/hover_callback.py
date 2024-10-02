from typing import Any, Callable, cast
import vtk
import pyvista as pv

OnPointHover = Callable[[tuple[float, float, float]], None]

class HoverInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    callback: OnPointHover
    def __init__(self, plotter: pv.Plotter, callback: OnPointHover):
        super().__init__()
        self.callback = callback
        self.AddObserver("MouseMoveEvent", self.on_mouse_move) # type: ignore
        self.plotter = plotter
        self.cell_picker = vtk.vtkCellPicker()
        self.cell_picker.SetTolerance(0.01)  # Adjust the tolerance as needed

    def on_mouse_move(self, obj: Any, event: Any):
        # Get the mouse position in display coordinates
        x, y = self.plotter.iren.get_event_position()
        
        # Perform the pick operation
        picker = self.cell_picker
        picker.Pick(x, y, 0, self.plotter.renderer)
        worldPosition = picker.GetPickPosition()

        self.callback(worldPosition)

        # Call parent method to handle other interactions
        self.OnMouseMove()
    
def on_world_hover(plotter: pv.Plotter, callback: OnPointHover):
    style = HoverInteractorStyle(plotter, callback)
    interactor = cast(vtk.vtkRenderWindowInteractor, plotter.iren.interactor)
    interactor.SetInteractorStyle(style)