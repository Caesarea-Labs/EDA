import numpy as np
import gdspy
import os
import cv2
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import shapely

def poly_intersection(A,B):
    #this function will return the intersection of the two polygons
    if A.intersects(B)==False:
        return False ,[]
    else:
        p=A.intersection(B)
        cord = [] # A list to contain the polygon arays
        if p.geom_type == 'Polygon':
            xx, yy = p.exterior.coords.xy
            A =np.array([xx.tolist(),yy.tolist()]).transpose()
            cord.append(A)
        elif p.geom_type == 'MultiPolygon':
            for pi in p.geoms:
                xx, yy = pi.exterior.coords.xy
                A =np.array([xx.tolist(),yy.tolist()]).transpose()
                cord.append(A)
    return True, cord

def slice_gds(in_file, cell_name, bounding_box, out_file='out_slice.gds'):
    # Load the gds
    gds_lib = gdspy.GdsLibrary(infile=in_file)
    # Set the cell needed to slicing
    cell = gds_lib.cells[cell_name]
    # Build the polygon for for the bounding box
    section_bb = Polygon(bounding_box)  # Replace with your section coordinates
    #section_bb = Polygon([(493, 682), (493, 857), (788, 857), (788, 682)])
    # Extract polygons grouped by layer and datatype
    polygons_by_layer = cell.get_polygons(by_spec=True)

    # Filter polygons by bounding box
    filtered_polygons = {}
    test_poly = Polygon(bounding_box)

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
        sections.append(section_cell)
    sections.append(top_cell)
    chip_r.cells=sections

    # Optional: Save the section to a new GDS file
    gds_lib = gdspy.GdsLibrary()
    gds_lib.write_gds(out_file, cells=sections)
    return chip_r


def cost_reward(gds_file,reward_cells,cost_cells,x_c,y_c,W,H,resolution):
    mask_cost = np.zeros((W * resolution, H * resolution))
    mask_reward = np.zeros((W * resolution, H * resolution))
    for t in cost_cells:
        polygons = gds_file.cells[t].get_polygons()
        for p in polygons:
            ver = []
            for i in range(len(p)):
                ver.append([resolution * (p[i, 1] - y_c), resolution * (p[i, 0] - x_c)])
            ver = np.array(ver, dtype=int)
            cv2.fillPoly(mask_cost, pts=[ver], color=255)

    for t in reward_cells:
        polygons = gds_file.cells[t].get_polygons()
        for p in polygons:
            ver = []
            for i in range(len(p)):
                ver.append([resolution * (p[i, 1] - y_c), resolution * (p[i, 0] - x_c)])
            ver = np.array(ver, dtype=int)
            cv2.fillPoly(mask_reward, pts=[ver], color=255)

    return mask_reward, mask_cost