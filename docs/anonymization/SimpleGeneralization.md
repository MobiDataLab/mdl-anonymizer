# Simple Generalization
One of the strategies to anonymize trajectory datasets are based on mitigating the disclosure risk. This kind of 
strategies follow the utility-first anonymization approach. They do not provide any formal privacy guarantees but 
aim to reduce reidentification risks by applying different techniques, such as noise addition, generalization and 
coarsening with heuristic parameter choice. After the application of such techniques, the disclosure risk is calculated
(for some objective disclosure prevention, i.e., identity disclosure or attribute disclosure). If the obtained risk 
is still too high, the techniques are applied with more strict parameters. Several of these techniques can be applied 
both in the context of location-based services and in static trajectory microdata sets.

A naive approach is to hide the original locations by means of generalization, specifically, replacing exact 
positions in the trajectories by approximate positions, i.e., points by centroids of areas. If a tessellation file is
not provided, the method first builds a regular spatial tessellation which covers the whole bounding box of the dataset.
Then, we replace every location of the dataset with the centroid of the corresponding tile. If more than one consecutive
locations of the same trajectory lie in the same tile, we can choose keeping them with their original timestamps or 
aggregating them by computing the average of all these timestamps.


## Specific parameters

- tiles_filename (str, optional, default: None): Tiles files for tessellation (geojson or shapefile)
- tile_size (int, optional, default: 500): If a tiles file is not provided, a squared tessellation of size ‘tile_size’ is generated (in meters)
- overlapping_strategy (enumerate ("all", "one"), optional, default: "all"): If a several locations of the same trajectory end up in the same tile, keep all (“all”) or take just one and compute the average timestamp (“one”)

Please, visit the [examples folder](../../examples/configs/config_SimpleGeneralization.json) to find an example of config file 
for the Simple Generalization method.