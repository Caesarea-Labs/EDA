# import tkinter as tk
# from pyvista import Plotter
# from vtkmodules.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

# root = tk.Tk()
# root.title("PyVista with Tkinter")

# frame = tk.Frame(root)
# frame.pack(fill=tk.BOTH, expand=True)

# plotter = Plotter(off_screen=False, window_size=[400, 400])
# interactor = vtkTkRenderWindowInteractor(frame, rw=plotter.ren_win)
# interactor.pack(fill=tk.BOTH, expand=True)
# interactor.Start()

# root.mainloop()