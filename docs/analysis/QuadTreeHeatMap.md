# QuadTreeHeatMap
For analysing the locations density without compromising privacy, a k-anonymous heat map generation method has been implemented. This consists of dividing the map into a set of size-variant rectangular sectors containing at least k locations. The locations density for each sector represents the “heat” of that area.

The approach is based on quadtree spatial decomposition, which recursively divides the 2D space into groups of four rectangular sectors. Initially, the quadtree consists of a single empty rectangular sector. As locations from the dataset are inserted, if a sector contains enough locations, it is divided into four equally sized subsectors. In this way, denser areas will have smaller sectors. To generate the heatmap, a top-bottom processing of the quadtree sectors is performed to obtain a set of sectors containing at least k locations (k-anonymous). To satisfy this requirement in a straightforward way, if a sector (equivalent to a quadtree node) has a child with less than k locations, all the child sectors are ignored, and only the parent sector is added to the heatmap. Alternatively, we can try to merge the child sectors to get new sectors with at least k locations. Furthermore, a new quadtree can be created using the locations from the merged sectors, which may result in fine-grained (smaller) k-anonymous sectors. For each sector of the resulting heatmap, the number of locations it contains is divided by its area, obtaining its location density.


## Specific parameters

- min_k (int, optional, default: 5): Minimum number of locations allowed to coexist in a QuadTree sector
- min_sector_length (int, optional, default: 100): Minimum side length for a QuadTree sector (in meters)
- merge_sectors (Boolean, optional, default: True): If True, sector with an insufficient number of locations will be merged with neighbouring sectors
- merge_sectors (int, optional, default: min_k): Max number of locations allowed in a QuadTree sector before it is spli into 4 subsectors. Must be greater than min_k. 

Please, visit the [examples folder](../../examples/configs/config_QuadTreeHeatMap.json) to find an example of config file 
for the QuadTreeHeatMap method.

[^1]: J. Domingo-Ferrer, S. Martínez and David Sánchez, "Decentralized k-anonymization of trajectories via privacy-preserving tit-for-tat", 
Computer Communications, Vol. 190, pp. 57-68, Jun 2022, ISSN: 0140-3664.