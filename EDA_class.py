import numpy as np
import gdspy
import os
import cv2
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import shapely
import tqdm
import matplotlib.image
from geneticalgorithm import geneticalgorithm as ga
from slice_utilities import poly_intersection, slice_gds, cost_reward

class EDA:
    def __init__(self, file,top_cell):
        self.Chip = gdspy.GdsLibrary(infile=file) #Original GDS file
        self.Top_Cell_Name = top_cell
        self.Chip_BP =[] # Original GDS file cropped to BP
        self.Chip_BP_Signals = [] # Cropped GDS file seperated to signals
        self.Chip_BP_Signals_layer = []  # Cropped GDS file seperated to signals and layers
        self.Chip_BP_Signals_layer_unique = []
        self.Chip_BP_Signals_layer_unique2 = []
        self.BP = [] # Polygon used for cropping the original GDS file
        self.Metal_Layers = []
        self.Via_Layers = []
        self.Signals_for_eda = []
        self.resolution = 100
    def Set_BP(self,poly):
        self.BP=poly
    def Set_Metal_Layers(self,metal_layers):
        self.Metal_Layers = metal_layers
        self.Metal_Layers.sort()
    def Set_Via_Layers(self,via_layers):
        self.Via_Layers = via_layers
    def Set_Signals_Num(self , signals_list):
        self.Signals_for_eda = signals_list
    def Slice_GDS(self):
        # Set the cell needed to slicing
        cell = self.Chip.cells[self.Top_Cell_Name]
        # Extract polygons grouped by layer and datatype
        polygons_by_layer = cell.get_polygons(by_spec=True)

        # Initialize Filter polygons by bounding box
        filtered_polygons = {}
        # Build polygon for GDS slicing
        test_poly = Polygon(self.BP)
        for (layer, datatype), polygons in polygons_by_layer.items():
            for polygon in polygons:
                res, poly = poly_intersection(test_poly, Polygon(polygon))
                if res:
                    if (layer, datatype) not in filtered_polygons:
                        filtered_polygons[(layer, datatype)] = []
                    for p in poly:
                        filtered_polygons[(layer, datatype)].append(p)

        # Print the number of polygons found in each layer
        for (layer, datatype), polygons in filtered_polygons.items():
            print(f"Layer: {layer}, Datatype: {datatype}, Polygons: {len(polygons)}")
        # Create a new cell to hold the filtered polygons
        # section_cell = gdspy.Cell('SECTION_VIEW')
        chip_r = gdspy.GdsLibrary()

        # Add filtered polygons to the new cell
        sections = []
        top_cell = gdspy.Cell('top')
        for (layer, datatype), polygons in filtered_polygons.items():
            section_cell = gdspy.Cell(str((layer, datatype)))
            for polygon in polygons:
                section_cell.add(gdspy.Polygon(polygon, layer=layer, datatype=datatype))
                top_cell.add(gdspy.Polygon(polygon, layer=layer, datatype=datatype))
            # sections.append(section_cell)
            chip_r.add(section_cell)
        chip_r.add(top_cell)
        # sections.append(top_cell)
        # chip_r.cells = sections
        self.Chip_BP = chip_r
    def Slice_GDS_Signal_Layer(self):
        #Get the keys for the cropped chip
        cells_keys = list(self.Chip_BP.cells.keys())
        cells_keys.remove('top')
        top_cell = gdspy.Cell('top_metal')
        signal_num = 0
        chip_r = gdspy.GdsLibrary()
        for key in cells_keys:
            layer = eval(key)[0]
            if layer in self.Metal_Layers:
                cell = self.Chip_BP.cells[key]
                poly = cell.get_polygons()
                S = self.Signals_in_Layers(poly)
                for s in S:
                    signal_cell = gdspy.Cell(str([layer, signal_num]))
                    for p in s:
                        signal_cell.add(gdspy.Polygon(poly[p], layer=layer, datatype=signal_num))
                        top_cell.add(gdspy.Polygon(poly[p], layer=layer, datatype=signal_num))
                    signal_num += 1
                    chip_r.add(signal_cell)
            if layer in self.Via_Layers:
                cell = self.Chip_BP.cells[key]
                name = str([eval(key)[0],eval(key)[1]])
                cell.name = name
                chip_r.add(cell)
        chip_r.add(top_cell)
        self.Chip_BP_Signals_layer = chip_r
    def Signals_in_Layers(self,polyset):
        N = len(polyset)
        # Building a polygon list
        P = list()
        for n in range(N):
            P.append(Polygon(polyset[n]))
        # Building the connectivety matrix
        A = np.zeros((N, N), dtype=bool)
        for n in range(N):
            A[n, n] = True
            for m in range(n + 1, N):
                A[n, m] = P[n].intersects(P[m])
                A[m, n] = A[n, m]
        # Building the Signals List
        Signals = list()
        for n in range(N):
            if sum(A[n, :]) > 0:  # indicating this cell has not been used
                signal = list()  # creating a new signal
                signal.append(n)  # appending the current polygon
                A[n, n] = False  # indecating the the polygon has been added to sigmal
                A[:, n] = False  # removing the cell from
                ind_M = A[n, :].nonzero()[0].tolist()
                A[n, :] = False
                for m in ind_M:
                    signal.append(m)
                    A[m, m] = False
                    C = A[:, m].nonzero()[0]
                    for c in C:
                        ind_c = A[:, c].nonzero()[0].tolist()
                        for i in ind_c:
                            signal.append(i)
                            A[i, i] = False
                signal = list(set(signal))
                Signals.append(signal)
        return Signals
    def Check_via_Metal(self,poly, sig_poly):
        p1 = Polygon(poly)
        for i in range(len(sig_poly)):
            p2 = Polygon(sig_poly[i])
            if p2.intersects(p1):
                return True
        return False
    def Slice_GDS_Signal_unique(self):
        chip_signals = self.Chip_BP_Signals_layer
        cells_keys = list(chip_signals.cells.keys())
        cells_keys.remove('top_metal')
        SIGNALS = list()
        N_singals = 0
        # Building the Signals list
        for i in self.Via_Layers: #Looping over the via cells
            via_cell = chip_signals.cells[str([i, 0])]
            polygons = via_cell.get_polygons()
            for p in range(len(polygons)): #looping over the polygons in the via cell
                poly = polygons[p]
                signal_list = list()
                for key in cells_keys:
                    layer_num, signal_num = eval(key)
                    N_singals = max(N_singals, signal_num)
                    if layer_num in self.Metal_Layers:
                        sig_poly = chip_signals.cells[key].get_polygons()
                        res = self.Check_via_Metal(poly, sig_poly)
                        if res:
                            signal_list.append(signal_num)
                if len(signal_list) > 0:
                    signal_list = list(set(signal_list))
                    SIGNALS.append(signal_list)
        N_singals +=1
        #Building the signals connectivity matrix
        As = np.zeros((N_singals, N_singals), dtype=bool)
        for s in SIGNALS:
            for n in s:
                As[n, n] = True
                for m in s:
                    As[n, m] = True
                    As[m, n] = True
        # Building the Signals_c list which groups the signals
        Signals_c = list()
        for n in range(N_singals):
            if sum(As[n, :]) > 0:  # indicating this cell has not been used
                signal = list()  # creating a new signal
                signal.append(n)  # appending the current polygon
                As[n, n] = False  # indecating the the polygon has been added to sigmal
                As[:, n] = False  # removing the cell from
                ind_M = As[n, :].nonzero()[0].tolist()
                As[n, :] = False
                for m in ind_M:
                    signal.append(m)
                    As[n, m] = False
                    As[m, n] = False
                    C = As[:, m].nonzero()[0]
                    for c in C:
                        ind_c = As[:, c].nonzero()[0].tolist()
                        for i in ind_c:
                            signal.append(i)
                            As[:, i] = False
                            As[i, :] = False
                signal = list(set(signal))
                Signals_c.append(signal)

        cells_keys = list(chip_signals.cells.keys())
        chip_r = gdspy.GdsLibrary()
        for key in cells_keys:
            if key == 'top_metal':
                cell = chip_signals.cells[key]
                chip_r.add(cell)
            else:
                layer_num, signal_num = eval(key)
                if layer_num in self.Metal_Layers:
                    for s in Signals_c:
                        if (signal_num in s):
                            s.sort()
                            name = str((layer_num, signal_num, s[0]))
                            cell = chip_signals.cells[key]
                            cell.name = name
                            chip_r.add(cell)

                else:
                    cell = chip_signals.cells[key]
                    chip_r.add(cell)
        self.Chip_BP_Signals_layer_unique = chip_r

        # Getting the number of signals
    def Slice_GDS_Signal_Layer_Unique(self):
        chip_signals = self.Chip_BP_Signals_layer_unique
        cells_keys = list(chip_signals.cells.keys())
        chip_r = gdspy.GdsLibrary()
        cells_signals = list()
        uni_sig = list()
        check_cell = gdspy.Cell('check')
        for key in cells_keys:
            if key == 'top_metal':
                cell = chip_signals.cells[key]
                chip_r.add(cell)
                chip_r.add(check_cell)
            elif (len(eval(key)) > 2):
                layer_num, signal_num, unique_signals = eval(key)
                if [layer_num, unique_signals] in uni_sig:
                    pass
                else:
                    signal_cell = gdspy.Cell(str((layer_num, unique_signals,0)))
                    uni_sig.append([layer_num, unique_signals])
                    for key2 in cells_keys:
                        if key2 == 'top_metal':
                            pass
                        elif (len(eval(key2)) > 2):
                            layer_num2, signal_num2, unique_signals2 = eval(key2)
                            if (layer_num == layer_num2 and unique_signals == unique_signals2):
                                poly = chip_signals.cells[key2].get_polygons()
                                for p in poly:
                                    signal_cell.add(gdspy.Polygon(p))
                                    check_cell.add(gdspy.Polygon(p))
                    #             cell.name=str(unique_signals)
                    chip_r.add(signal_cell)
        self.Chip_BP_Signals_layer_unique2 = chip_r
    def Slice_GDS_Signal(self):
        chip_signals = self.Chip_BP_Signals_layer_unique
        cells_keys = list(chip_signals.cells.keys())
        chip_r = gdspy.GdsLibrary()
        cells_signals = list()
        uni_sig = list()
        check_cell = gdspy.Cell('check_u')
        for key in cells_keys:
            if key == 'top_metal':
                cell = chip_signals.cells[key]
                chip_r.add(cell)
                chip_r.add(check_cell)
            elif (len(eval(key)) > 2):
                layer_num, signal_num, unique_signals = eval(key)
                if unique_signals in uni_sig:
                    pass
                else:
                    signal_cell = gdspy.Cell(str(unique_signals))
                    uni_sig.append(unique_signals)
                    if layer_num in self.Metal_Layers:
                        #                 cell = chip_signals.cells[key]
                        for key2 in cells_keys:
                            if key2 == 'top_metal':
                                pass
                            elif (len(eval(key2)) > 2):
                                layer_num2, signal_num2, unique_signals2 = eval(key2)
                                if (unique_signals == unique_signals2):
                                    poly = chip_signals.cells[key2].get_polygons()
                                    for p in poly:
                                        signal_cell.add(gdspy.Polygon(p))
                                        check_cell.add(gdspy.Polygon(p))
                    #             cell.name=str(unique_signals)
                    chip_r.add(signal_cell)
        self.Chip_BP_Signals = chip_r
    def Slice_Signals(self, save=False):
        self.Slice_GDS_Signal_Layer()
        self.Slice_GDS_Signal_unique()
        self.Slice_GDS_Signal_Layer_Unique()
        self.Slice_GDS_Signal()
        if (save):
            self.Chip_BP_Signals.write_gds('GDS_Signals_global.gds')
            self.Chip_BP_Signals_layer_unique2.write_gds('GDS_Signals_layers.gds')
    def Build_Reward_mask(self,signal_num):
        print({f'signal number is {signal_num}'})
        chip_signals = self.Chip_BP_Signals_layer_unique2
        x=list()
        y=list()
        for xy in self.BP:
            x.append(xy[0])
            y.append(xy[1])
        x_min = min(x)
        x_max = max(x)
        y_min = min(y)
        y_max = max(y)
        w = x_max - x_min
        h = y_max - y_min
        mask_reward_list = list()
        for l in self.Metal_Layers:
            mask_reward_list.append(np.zeros((w * self.resolution, h * self.resolution)))
        keys = list(chip_signals.cells.keys())
        keys.remove('check')
        keys.remove('top_metal')
        min_layer = min(self.Metal_Layers) + 1
        max_layer = max(self.Metal_Layers) + 1
        for layer in self.Metal_Layers:
            e_key = str((layer, signal_num, 0))
            r = (layer - min_layer + 1) / (max_layer - min_layer +1)
            if e_key in keys:
                polygons = chip_signals.cells[e_key].get_polygons()
                for p in polygons:
                    ver = []
                    for i in range(len(p)):
                        ver.append([self.resolution * (p[i, 1] - y_min), self.resolution * (p[i, 0] - x_min)])
                    ver = np.array(ver, dtype=int)
                    for i in range(len(self.Metal_Layers)):
                        if (self.Metal_Layers[i] == layer):
                            cv2.fillPoly(mask_reward_list[i], pts=[ver], color=r)
        return mask_reward_list
    def Build_Reward_masks(self):
        self.reward_mask1 = self.Build_Reward_mask(self.Signals_for_eda[0])
        self.reward_mask2 = self.Build_Reward_mask(self.Signals_for_eda[1])
    def Build_Cost_mask(self):
        chip_signals = self.Chip_BP_Signals_layer_unique2
        x = list()
        y = list()
        for xy in self.BP:
            x.append(xy[0])
            y.append(xy[1])
        x_min = min(x)
        x_max = max(x)
        y_min = min(y)
        y_max = max(y)
        w = x_max - x_min
        h = y_max - y_min
        mask_cost_list = list()
        for l in self.Metal_Layers:
            mask_cost_list.append(np.zeros((w * self.resolution, h * self.resolution)))
        keys = list(chip_signals.cells.keys())
        keys.remove('check')
        keys.remove('top_metal')
        min_layer = min(self.Metal_Layers) + 1
        max_layer = max(self.Metal_Layers) + 1
        for key in keys:
            layer, sig_num, foo = eval(key)
            r = (layer - min_layer + 1) / (max_layer - min_layer)
            if (sig_num in self.Signals_for_eda):
                pass
            else:
                polygons = chip_signals.cells[key].get_polygons()
                for p in polygons:
                    ver = []
                    for i in range(len(p)):
                        ver.append([self.resolution * (p[i, 1] - y_min), self.resolution * (p[i, 0] - x_min)])
                    ver = np.array(ver, dtype=int)
                    for i in range(len(self.Metal_Layers)):
                        if (self.Metal_Layers[i] == layer):
                            cv2.fillPoly(mask_cost_list[i], pts=[ver], color=r)
        self.cost_mask = mask_cost_list
    def plot_results(self,X,w):
        x = list()
        y = list()
        for xy in self.BP:
            x.append(xy[0])
            y.append(xy[1])
        x_min = min(x)
        x_max = max(x)
        y_min = min(y)
        y_max = max(y)
        x1, y1, l1, x2, y2, l2 = X
        x1_g = x1 / self.resolution + x_min
        y1_g = y1 / self.resolution + y_min
        x2_g = x2 / self.resolution + x_min
        y2_g = y2 / self.resolution + y_min

        r = w / self.resolution
        res_poly1 = [[x1_g - r, y1_g - r],
                     [x1_g - r, y1_g + r],
                     [x1_g + r, y1_g + r],
                     [x1_g + r, y1_g - r],
                     [x1_g - r, y1_g - r]]

        res_poly2 = [[x2_g - r, y2_g - r],
                     [x2_g - r, y2_g + r],
                     [x2_g + r, y2_g + r],
                     [x2_g + r, y2_g - r],
                     [x2_g - r, y2_g - r]]
        chip_r = gdspy.GdsLibrary(infile='GDS_Signals_global.gds')
        chip_r.cells['0'].add(gdspy.Polygon(res_poly1, layer=80, datatype=555))
        chip_r.cells['5'].add(gdspy.Polygon(res_poly2, layer=80, datatype=555))
        chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly1, layer=80, datatype=555))
        chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly2, layer=80, datatype=555))
        chip_r.write_gds('GDS_Signals_global_results.gds')



















