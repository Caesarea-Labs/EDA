Running GA on signals 0 and 5, on the lior GDS file in bounds [(1200, 730), (1200, 775), (1390, 775), (1390, 762), (1210, 762), (1210, 730)]:

| Name                         | Time           | Command                                                                        |   
|------------------------------|----------------|--------------------------------------------------------------------------------| 
| shapely `Polygon.intersects` | 4.46s (+-1.22) | `pytest -rP benchmarks/test_benchmark_ga.py::test_benchmark_geneticalgorithm2` | 
|                              |                |                                                                                | 
|                              |                |                                                                                |   

Calculating the total intersecting area of a rectangle with many polygons, with 20 rectangle-polygons  cases. 

| Name                                          | Time             | Command                                                                                       |   
|-----------------------------------------------|------------------|-----------------------------------------------------------------------------------------------| 
| shapely with unary_union                      | 1.95ms (+- 5.04) | `pytest -rP benchmarks/test_benchmark_intersection_area.py::test_benchmark_intersection_area` | 
| shapely without unary_union                   | 1.31ms (+- 3.68) |                                                                                               | 
| shapely without unary_union without filtering | 1.22ms (+- 5.77) |                                                                                               |   

<!-- 0.0013191012620925903 +-0.00368125159740448 -->

<!-- 0.0012218593597412108 +-0.005777871704101562 -->