from pathlib import Path
from typing import cast

from gdstk import Polygon
from gds_to_layout import CPolygon, parse_gds_layout
from layout import Layout
import numpy as np
import cv2
from numpy.typing import NDArray
from geneticalgorithm import geneticalgorithm as ga
import matplotlib.pyplot as plt

resolution = 100


def Build_Reward_mask(layout: Layout, bounding_box: CPolygon, signal_num: int) -> list[NDArray[np.float64]]:
    print({f'signal number is {signal_num}'})
    layer_count = layout.layer_count()
    layers = layout.metals_by_layer()
    x = []
    y = []
    for xy in bounding_box:
        x.append(xy[0])
        y.append(xy[1])
    x_min = min(x)
    x_max = max(x)
    y_min = min(y)
    y_max = max(y)
    w = x_max - x_min
    h = y_max - y_min
    mask_reward_list: list[NDArray[np.float64]] = list()
    for _ in range(layout.layer_count()):
        mask_reward_list.append(np.zeros((w * resolution, h * resolution)))

    min_layer = 1
    max_layer = layer_count
    for layer, metals in enumerate(layers):
        r: cv2.typing.Scalar = cast(cv2.typing.Scalar, (layer - min_layer + 1) / (max_layer - min_layer + 1))
        for metal in metals:
            # I care about the two signals
            if metal.layer != signal_num:
                continue
            polygon = metal.vertices
            ver = []
            for i in range(len(polygon)):
                vertex = polygon[i]
                ver.append([resolution * (vertex.y - y_min), resolution * (vertex.x - x_min)])
            ver = np.array(ver, dtype=int)
            cv2.fillPoly(img=mask_reward_list[layer], pts=[ver], color=r)
    return mask_reward_list


Gausian_Kernal_size = 11


def Build_Cost_mask(layout: Layout, bounding_box: CPolygon, target_signal_a: int, target_signal_b: int) -> list[NDArray[np.float64]]:
    # chip_signals = self.Chip_BP_Signals_layer_unique2
    layer_count = layout.layer_count()
    x = list()
    y = list()
    for xy in bounding_box:
        x.append(xy[0])
        y.append(xy[1])
    x_min = min(x)
    x_max = max(x)
    y_min = min(y)
    y_max = max(y)
    w = x_max - x_min
    h = y_max - y_min
    mask_cost_list = list()
    for _ in range(layout.layer_count()):
        mask_cost_list.append(np.zeros((w * resolution, h * resolution)))
    # keys = list(chip_signals.cells.keys())
    # keys.remove('check')
    # keys.remove('top_metal')
    min_layer = 1
    max_layer = layer_count

    for layer, metals in enumerate(layout.metals_by_layer()):
        r: cv2.typing.Scalar = cast(cv2.typing.Scalar, (layer - min_layer + 1) / (max_layer - min_layer))
        for metal in metals:
            # I care about other layers
            if metal.layer == target_signal_a or metal.layer == target_signal_b:
                continue

            polygon = metal.vertices
            ver = []
            for i in range(len(polygon)):
                vertex = polygon[i]
                ver.append([resolution * (vertex.y - y_min), resolution * (vertex.x - x_min)])
            ver = np.array(ver, dtype=int)
            cv2.fillPoly(img=mask_cost_list[layer], pts=[ver], color=r)

    cost_mask = list()
    for i in range(len(mask_cost_list)):
        cost_mask.append(cv2.GaussianBlur(mask_cost_list[i], (Gausian_Kernal_size, Gausian_Kernal_size), 0))

    return cost_mask


# def plot_results(bounding_box: CPolygon, X, w):
#     x = list()
#     y = list()
#     for xy in bounding_box:
#         x.append(xy[0])
#         y.append(xy[1])
#     x_min = min(x)
#     x_max = max(x)
#     y_min = min(y)
#     y_max = max(y)
#     x1, y1, l1, x2, y2, l2 = X
#     x1_g = x1 / resolution + x_min
#     y1_g = y1 / resolution + y_min
#     print(f'first via at x={x1_g} and y={y1_g}')
#     x2_g = x2 / resolution + x_min
#     y2_g = y2 / resolution + y_min
#     print(f'Second via at x={x2_g} and y={y2_g}')

#     r = w / resolution
#     res_poly1 = [[x1_g - r, y1_g - r],
#                  [x1_g - r, y1_g + r],
#                  [x1_g + r, y1_g + r],
#                  [x1_g + r, y1_g - r],
#                  [x1_g - r, y1_g - r]]

#     res_poly2 = [[x2_g - r, y2_g - r],
#                  [x2_g - r, y2_g + r],
#                  [x2_g + r, y2_g + r],
#                  [x2_g + r, y2_g - r],
#                  [x2_g - r, y2_g - r]]
#     chip_r =
#     chip_r = gdspy.GdsLibrary(infile='GDS_Signals_global.gds')
#     chip_r.cells[str(int(self.Signals_for_eda[0]))].add(gdspy.Polygon(res_poly1, layer=254))
#     chip_r.cells[str(int(self.Signals_for_eda[1]))].add(gdspy.Polygon(res_poly2, layer=255))
#     chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly1, layer=254))
#     chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly2, layer=255))
#     chip_r.write_gds('GDS_Signals_global_results.gds')
#     chip_r = gdspy.GdsLibrary(infile='GDS_Signals_in_Layers.gds')
#     L1 = 'L-' + str(int(l1))
#     L2 = 'L-' + str(int(l2))
#     chip_r.cells[L1].add(gdspy.Polygon(res_poly1, layer=254))
#     chip_r.cells[L2].add(gdspy.Polygon(res_poly2, layer=255))
#     chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly1, layer=254))
#     chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly2, layer=255))
#     chip_r.write_gds('GDS_Signals_in_Layers_results.gds')


# def Sample_from_poly(polygon: CPolygon, x_g: float, y_g: float, B):
#     x = [point[0] for point in polygon]
#     y = [point[1] for point in polygon]
#     x_min = min(x)
#     x_max = max(x)
#     y_min = min(y)
#     y_max = max(y)
#     x = (np.random.uniform(x_min, x_max)-x_g)*resolution
#     y = (np.random.uniform(y_min, y_max)-y_g)*resolution
#     if (x < B[0, 0]):
#         x = B[0, 0]
#     elif (x > B[0, 1]):
#         x = B[0, 1]
#     if (y < B[1, 0]):
#         y = B[1, 0]
#     elif (y > B[1, 1]):
#         y = B[1, 1]
#     return x, y


def Generate_Initial_Population(layout: Layout, bounding_box: CPolygon, Num: int, bounds: NDArray[np.float64], target_signal_a: int, target_signal_b: int) -> NDArray[np.float64]:
    """
    Returns a 2d float array composing the initial tested points. 
    The array has 6 columns, as follows:
    [
        [x_a, y_a, layer_a,  x_b, y_b, layer_b],
        ...
    ]
    Where (x_a, y_a, layer_a) is a random point on the first signal, and (x_b, y_b, layer_b) is a random point on the second signal. 
    """


# def Generate_Initial_Population(layout: Layout, bounding_box: CPolygon, Num: int, bounds: NDArray[np.float64], target_signal_a: int, target_signal_b: int):
#     layer_count = layout.layer_count()
#     metal_layers = layout.metals_by_layer()
#     x = list()
#     y = list()
#     for xy in bounding_box:
#         x.append(xy[0])
#         y.append(xy[1])
#     x_g = min(x)
#     y_g = min(y)
#     keys = list(self.Chip_BP_Signals_layer_unique2.cells.keys())
#     # Elements for the first signal
#     Sample_in_layer: NDArray[np.bool] = np.zeros(layer_count, dtype=bool)
#     for layer, metals in enumerate(metal_layers):
#         if any([metal.signal_index == target_signal_a for metal in metals]):
#             Sample_in_layer[layer] = True
#     # for i in range(len(self.Metal_Layers)):
#     #     test_key = str((self.Metal_Layers[i], self.Signals_for_eda[0], 0))
#     #     if test_key in keys:
#     #         Sample_in_layer[i] = True
#     Sample_in_layer_2 = Sample_in_layer * int(Num / sum(Sample_in_layer))
#     print(Sample_in_layer_2)
#     Samples = list()  # np.array(size=(Num,3),dtype=float)
#     for i, metals in enumerate(metal_layers):
#         if Sample_in_layer_2[i] > 0:
#             relevant_metals = [metal for metal in metals if metal.signal_index == target_signal_a]
#             for metal in metals:
#                 if metal.signal_index == target_signal_a:
#                     Poly = metal.vertices
#                     p = len(Poly)
#                     for j in range(Sample_in_layer_2[i]):
#                         h = np.random.randint(p)
#                         # print('layer={}, poly_num={} of {}'.format(l, h, p))
#                         x, y = Sample_from_poly(Poly[h], x_g, y_g, bounds[0:2, :])
#                         Samples.append([x, y, i])

#     for i in range(len(self.Metal_Layers)):
#         l = self.Metal_Layers[i]
#         if Sample_in_layer[i] > 0:
#             test_key = str((self.Metal_Layers[i], self.Signals_for_eda[0], 0))
#             Poly = self.Chip_BP_Signals_layer_unique2.cells[test_key].get_polygons()
#             p = len(Poly)
#             for j in range(Sample_in_layer[i]):
#                 h = np.random.randint(p)
#                 # print('layer={}, poly_num={} of {}'.format(l, h, p))
#                 x, y = self.Sample_from_poly(Poly[h],x_g, y_g ,bounds[0:2,:] )
#                 Samples.append([x, y, l])

#     for i in range(Num-len(Samples)):
#         x = np.random.uniform(bounds[0, 0], bounds[0, 1])
#         y = np.random.uniform(bounds[1, 0], bounds[1, 1])
#         l = np.random.randint(bounds[2, 0], bounds[2, 1])
#         Samples.append([x, y, l])
    # S1 = np.array(Samples)
    # arr = np.arange(Num)
    # np.random.shuffle(arr)
    # S1 = S1[arr, :]

#     # Elements for the Second signal
#     Sample_in_layer_3 = np.zeros(len(self.Metal_Layers), dtype=bool)
#     for i in range(len(self.Metal_Layers)):
#         test_key = str((self.Metal_Layers[i], self.Signals_for_eda[1], 0))
#         if test_key in keys:
#             Sample_in_layer_3[i] = True
#     Sample_in_layer_4 = Sample_in_layer_3 * int(Num / sum(Sample_in_layer_3))
#     print(Sample_in_layer_4)
#     Samples = list()  # np.array(size=(Num,3),dtype=float)
#     for i in range(len(self.Metal_Layers)):
#         l = self.Metal_Layers[i]
#         if Sample_in_layer_4[i] > 0:
#             test_key = str((self.Metal_Layers[i], self.Signals_for_eda[1], 0))
#             Poly = self.Chip_BP_Signals_layer_unique2.cells[test_key].get_polygons()
#             p = len(Poly)
#             for j in range(Sample_in_layer_4[i]):
#                 h = np.random.randint(p)
#                 # print('layer={}, poly_num={} of {}'.format(l, h, p))
#                 x, y = self.Sample_from_poly(Poly[h], x_g, y_g, bounds[0:2, :])
#                 Samples.append([x, y, l])
#     for i in range(Num - len(Samples)):
#         x = np.random.uniform(bounds[0, 0], bounds[0, 1])
#         y = np.random.uniform(bounds[1, 0], bounds[1, 1])
#         l = np.random.randint(bounds[2, 0], bounds[2, 1])
#         Samples.append([x, y, l])
#     S2 = np.array(Samples)
#     arr = np.arange(Num)
#     np.random.shuffle(arr)
#     S2 = S2[arr, :]
#     S = np.concatenate((S1, S2), axis=1)
#     return S


if __name__ == "__main__":
    bounds: CPolygon = [(1200, 730), (1200, 775), (1390, 775), (1390, 762), (1210, 762), (1210, 730)]
    layout = parse_gds_layout(
        Path("test_gds_1.gds"),
        bounds,
        metal_layers={61, 62, 63, 64, 65, 66},
        via_layers={70, 71, 72, 73, 74}
    )
    reward_mask1 = Build_Reward_mask(layout, bounds, signal_num=0)
    reward_mask2 = Build_Reward_mask(layout, bounds, signal_num=5)
    cost_mask = Build_Cost_mask(layout, bounds, 0, 5)
    cost_mask[0][0]
    W, H = cost_mask[0].shape
    metal_layers = range(layout.layer_count())
    varbound = np.array([[20, W-20], [20, H-20], [61, 66], [20, W-20], [20, H-20], [61, 66]])
    Num_generation = 10000
    S = Generate_Initial_Population(layout, bounds, Num_generation, varbound, 0, 5)

    algorithm_param = {'initial_population':S,\
                   'max_num_iteration': 100,\
                   'population_size':Num_generation,\
                   'mutation_probability':0.1,\
                   'elit_ratio': 0.01,\
                   'crossover_probability': 0.5,\
                   'parents_portion': 0.3,\
                   'crossover_type':'uniform',\
                   'max_iteration_without_improv':None}
    
    def cost_reward(x: float,y: float,l: int,s: int):
        ind_l=(metal_layers).index(l)
        cost= 0
        for i in range(ind_l,len(metal_layers)):
            layer_values = cost_mask[i]
            start_row = (x-20)
            start_col = (x+20)
            end_row = (y-20)
            end_col = (y+20)
            value = layer_values[start_row:start_col,end_row:end_col]
            first_sum: NDArray[np.float64] = cast(  NDArray[np.float64], sum(value))

            cost += sum(first_sum)
        reward = 0
        if s==1:
            reward = sum(sum(reward_mask1[ind_l][(x-20):(x+20),(y-20):(y+20)])) # type: ignore
            for i in range(ind_l,len(metal_layers)):
                cost += sum(sum(reward_mask2[i][(x-20):(x+20),(y-20):(y+20)])) # type: ignore
        elif s==2:
            reward = sum(sum(reward_mask2[ind_l][(x-20):(x+20),(y-20):(y+20)])) # type: ignore
            for i in range(ind_l,len(metal_layers)):
                cost += sum(sum(reward_mask1[i][(x-20):(x+20),(y-20):(y+20)])) # type: ignore
        
        return cost,reward
    
    def cost_func(X: list[float]):
        x1=int(X[0])
        y1=int(X[1])
        l1=int(X[2])
        x2=int(X[3])
        y2=int(X[4])
        l2=int(X[5])
        cost1, reward1 = cost_reward(x1,y1,l1,1)
        cost2, reward2 = cost_reward(x2,y2,l2,2)
        cost = cost1+cost2
        reward = 100*(reward1+reward2)
        L=((x1-x2)**2+(y1-y2)**2)**0.5
        L_cost = (L -80)**2#to prevent overlap between the two vias
        alpha=0.1
        if (cost>0 or reward1==0 or reward2==0):
            return cost
        else:
            return -reward + alpha*L_cost
    
    varbound=np.array([[20,W-20],[20,H-20],[61,66],[20,W-20],[20,H-20],[61,66]])
    vartype=np.array([['real'],['real'],['int'],['real'],['real'],['int']])
    model=ga(function=cost_func,dimension=6,variable_type_mixed=vartype,variable_boundaries=varbound,algorithm_parameters=algorithm_param)
    model.run()

    x1=S[:,0]
    y1=S[:,1]
    x2=S[:,3]
    y2=S[:,4]

    plt.plot(x1,y1,'*r',x2,y2,'*b')
    plt.show()
    
    