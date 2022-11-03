from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.pyqtree import Index, _QuadTree
import logging
from tqdm import tqdm
from shapely import geometry
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import numpy as np

DEFAULT_VALUES = {
    "min_k": 5,
    "max_locations": 10,
    "max_depth": 30,
    "merge_sectors": True
}


class QuadTreeHeatMap:
    """Creates a heatmap of the data via a QuadTree (Klinger, A., & Dyer, C. R. 1976, https://www.sciencedirect.com/science/article/abs/pii/S0146664X76800068).
    Similar approach to the used in https://www.idescat.cat/sort/sort411/41.1.7.lagonigro-etal.prov.pdf
    """

    def __init__(self, dataset: Dataset, min_k: int, max_locations: int,
                 max_depth: int, merge_sectors: bool):
        """
        Parameters
        ----------
        dataset : Dataset
            Dataset to anonymize.
        min_k : int
            Minimum number of locations allowed co-exist in a QuadTree sector.
        max_locations : int
            Maximum number of locations allowed in a QuadTree sector before it is split.
            It must be greater than min_k.
        max_depth : int
            Maximum depth allowed for the QuadTree.
        merge_sectors : bool
            If True, sectors with an insufficient number of locations will be merged with neighboring sectors.
            This should improve utility.
        """
        self.dataset = dataset
        self.min_k = min_k
        self.max_locations = max_locations
        assert max_locations > min_k
        self.max_depth = max_depth
        self.merge_sectors = merge_sectors
        print("INIT", self.merge_sectors)
        self.heatmap_nodes = None
        self.anonymized_dataset = None

    def run(self):
        # Reset heatmap and transform dataset to NumPy
        np_dataset = self.dataset.to_numpy()

        # Initialize QuadTree with bounding box
        min_x = min(np_dataset[:, 0])
        min_y = min(np_dataset[:, 1])
        max_x = max(np_dataset[:, 0])
        max_y = max(np_dataset[:, 1])
        self.qtree = Index(bbox=(min_x, min_y, max_x, max_y),
                           max_items=self.max_locations,
                           max_depth=self.max_depth)

        # Insert locations
        logging.info("Inserting locations to QuadTree...")
        for [x, y] in tqdm(np_dataset[:, :2]):
            # Insert (Object, Bounding box) to QuadTree
            self.qtree.insert((x, y),  # Object
                              (x, y, x, y))  # Bounding box

        # Get QuadTree sectors that have at least min_k locations
        logging.info("Transforming QuadTree to K-anonymous heatmap...")
        self.heatmap_nodes = self.qtree_to_heatmap(self.qtree)
        logging.info("Done!")

        # Transform heatmap to GeoPandasFrame
        logging.info("Generating GeoPandasFrame...")
        gdf_dict = {"geometry": [], "n_location": []}
        for (bbox, n_locations) in self.heatmap_nodes:
            point_list = [[bbox[1], bbox[0]], [bbox[1], bbox[2]], [bbox[3], bbox[2]], [bbox[3], bbox[0]]]
            polygon = geometry.Polygon(point_list)
            gdf_dict["geometry"].append(polygon)
            gdf_dict["n_location"].append(n_locations)
        gdf = GeoDataFrame(gdf_dict)
        self.anonymized_dataset = gdf
        logging.info("Done!")

        # Plotting # TODO: Remove
        plt.scatter(np_dataset[:, 1], np_dataset[:, 0])
        fig, ax = plt.subplots(1, 1)
        gdf.plot(column='n_location', cmap='OrRd', ax=ax, legend=True)
        bdf = GeoDataFrame(geometry=gdf.boundary)
        bdf.plot()
        plt.show()

    def qtree_to_heatmap(self, qtree_elem):
        heatmap = []

        # If no children and enough locations, add *parent* to heatmap
        if len(qtree_elem.children) == 0:
            n_parent_locations = len(qtree_elem)
            if n_parent_locations >= self.min_k:  # If enough locations
                heatmap.append((self.get_bbox(qtree_elem), n_parent_locations))
        # Otherwise, check children
        else:
            # If merge sectors
            if self.merge_sectors:
                if qtree_elem == self.qtree: print("MERGING")
                # Try to merge children with not enough locations
                children_idxs = list(range(len(qtree_elem.children)))
                children_nlocs = [len(child) for child in qtree_elem.children]
                children_idxs_by_nlocs = [idx for _, idx in sorted(zip(children_nlocs, children_idxs))]  # Ascending
                idx = 0
                while idx < len(children_idxs_by_nlocs):
                    child_idx = children_idxs_by_nlocs[idx]
                    child = qtree_elem.children[child_idx]
                    n_child_locations = len(child)

                    # If no locations, ignore
                    if n_child_locations == 0:
                        # Avoid mergings with it
                        children_idxs_by_nlocs.remove(child_idx)
                        idx -= 1
                    # If not enough locations, try to merge with neighbours
                    elif n_child_locations < self.min_k:
                        impossible_k_anonymity = False

                        # Get neighbours indexes
                        # Children order: Bottom left, top left, bottom right, top right. So neightbours are at | +1,+2 | +2,+3 | +1,+2 | +2,+3
                        if child_idx % 2 == 0:  # If pair
                            first_neigh = (child_idx + 1) % 4
                            second_neigh = (child_idx + 2) % 4
                        else:  # If not pair
                            first_neigh = (child_idx + 2) % 4
                            second_neigh = (child_idx + 3) % 4

                        # If there are available neighbours for merging
                        neighbours_idxs = [neigh_idx for neigh_idx in [first_neigh, second_neigh] if
                                           neigh_idx in children_idxs_by_nlocs]
                        if len(neighbours_idxs) > 0:
                            # Sort neighbours by number of locations in ascending. A heuristic for better (not optimal) utility.
                            neighbours_nlocs = [children_nlocs[neigh_idx] for neigh_idx in neighbours_idxs]
                            neighbours_by_nlocs = [neigh_idx for _, neigh_idx in
                                                   sorted(zip(neighbours_nlocs, neighbours_idxs))]

                            # Try to merge with neighbours by #locations
                            is_merged = False
                            for neigh_idx in neighbours_by_nlocs:
                                # If it #locations is enough, create *group* and add to heatmap
                                total_locations = n_child_locations + children_nlocs[neigh_idx]
                                if total_locations >= self.min_k:
                                    neighbour = qtree_elem.children[neigh_idx]
                                    bbox_1 = self.get_bbox(child)
                                    bbox_2 = self.get_bbox(neighbour)
                                    bbox = (min(bbox_1[0], bbox_2[0]),
                                            min(bbox_1[1], bbox_2[1]),
                                            max(bbox_1[2], bbox_2[2]),
                                            max(bbox_1[3], bbox_2[3]))
                                    heatmap.append((bbox, total_locations))

                                    # Avoid repeating mergings
                                    children_idxs_by_nlocs.remove(child_idx)
                                    children_idxs_by_nlocs.remove(neigh_idx)
                                    idx -= 1

                                    # End of loop
                                    is_merged = True
                                    break

                            # If it has not been merged
                            if not is_merged:
                                impossible_k_anonymity = True

                        # Otherwise, there is no merging possible
                        else:
                            impossible_k_anonymity = True

                        # If there is not merging that ensures k-anonymity, add *parent* to heatmap and break
                        if impossible_k_anonymity:
                            n_parent_locations = len(qtree_elem)
                            heatmap = []  # Reset heatmap
                            heatmap = [(self.get_bbox(qtree_elem), n_parent_locations)]  # Add parent
                            break

                    # If child has enough locations, search inside
                    else:
                        heatmap += self.qtree_to_heatmap(child)

                        # Avoid mergings with it
                        children_idxs_by_nlocs.remove(child_idx)
                        idx -= 1

                    # Increment index
                    idx += 1
            # If no merge sectors
            else:
                if qtree_elem == self.qtree: print("NO MERGING")
                for child in qtree_elem.children:
                    n_child_locations = len(child)
                    # If not enough locations
                    if n_child_locations < self.min_k:
                        # If zero locations, ignore
                        if n_child_locations == 0:
                            pass
                        # Otherwise, ONLY add *parent* to heatmap and break
                        else:
                            n_parent_locations = len(qtree_elem)
                            heatmap = []  # Reset heatmap of nodes from other children
                            heatmap = [(self.get_bbox(qtree_elem), n_parent_locations)]  # Add parent
                            break
                    # If child has enough locations, search inside
                    else:
                        heatmap += self.qtree_to_heatmap(child)



        return heatmap

    def get_bbox(self, qtree_elem: _QuadTree):
        (center_x, center_y) = qtree_elem.center
        half_width = qtree_elem.width / 2.0
        min_x, max_x = center_x - half_width, center_x + half_width
        half_height = qtree_elem.height / 2.0
        min_y, max_y = center_y - half_height, center_y + half_height
        bbox = (min_x, min_y, max_x, max_y)
        return bbox

    def get_anonymized_dataset(self) -> Dataset:
        """Returns
        -------
        anonymized_dataset : Dataset
            The anonymized dataset computed at the run method"""
        return self.anonymized_dataset

    @staticmethod
    def get_instance(data):
        required_fields = ["min_k", "max_locations", "max_depth", "merge_sectors"]
        values = {}

        for field in required_fields:
            values[field] = data.get(field)
            if values[field] is None:
                logging.info(f"No '{field}' provided. Using {DEFAULT_VALUES[field]}.")
                values[field] = DEFAULT_VALUES[field]

        dataset = Dataset()
        dataset.load_from_scikit(data.get("input_file"), min_locations=1, datetime_key="timestamp")
        dataset.filter_by_speed()

        return QuadTreeHeatMap(dataset, values['min_k'], values['max_locations'],
                               values["max_depth"], values["merge_sectors"])
