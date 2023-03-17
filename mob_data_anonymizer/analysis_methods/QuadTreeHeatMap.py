from mob_data_anonymizer.analysis_methods.AnalysisMethodInterface import AnalysisMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.pyqtree import Index, _QuadTree
import logging
from tqdm import tqdm
from shapely import geometry
from shapely.ops import transform
from geopandas import GeoDataFrame
import pyproj
from functools import partial
from haversine import haversine, Unit
import math

DEFAULT_VALUES = {
    "min_k": 5,
    "min_sector_length": 100,
    "split_n_locations": None,
    "merge_sectors": True
}


class QuadTreeHeatMap(AnalysisMethodInterface):
    """Creates a heatmap of the data via a QuadTree (Klinger, A., & Dyer, C. R. 1976, https://www.sciencedirect.com/science/article/abs/pii/S0146664X76800068)
    ensuring K-anonymity.
    Similar approach to the used in https://www.idescat.cat/sort/sort411/41.1.7.lagonigro-etal.prov.pdf
    """

    def __init__(self,
                 dataset: Dataset,
                 min_k: int = DEFAULT_VALUES['min_k'],
                 min_sector_length: int = DEFAULT_VALUES['min_sector_length'],
                 merge_sectors: bool = DEFAULT_VALUES['merge_sectors'],
                 split_n_locations: int = DEFAULT_VALUES['split_n_locations']
                 ):
        """
        Parameters
        ----------
        dataset : Dataset
            Dataset to anonymize.
        min_k : int
            Minimum number of locations allowed co-exist in a QuadTree sector.
            The algorithm ensures K-anonymity using this k.
        min_sector_length : int
            Minimum side length (in meters) for a QuadTree sector.
            Equivalent to minimum resolution.
            Due to the definition of the tree depth, empirical min_sector_length can be almost two times greater.
        merge_sectors : bool
            If True, sectors with an insufficient number of locations will be merged with neighboring sectors.
            This always preserves or enhances utility.
        split_n_locations : int
            Maximum number of locations allowed in a QuadTree sector before it is split into 4 subsectors.
            It must be greater than min_k. If lower or None, the value would be automatically set to min_k.
            A value of min_k is expected to be the bests in terms of utility.
        """
        self.dataset = dataset
        self.min_k = min_k
        self.min_sector_length = min_sector_length
        self.merge_sectors = merge_sectors

        if split_n_locations is None:
            logging.info(f"NOTE: split_n_locations is None, setting to min_k [{min_k}]")
            split_n_locations = min_k
        elif split_n_locations < min_k:
            logging.info(f"WARNING: split_n_locations [{split_n_locations}] lower than min_k [{min_k}], setting to min_k")
            split_n_locations = min_k
        self.split_n_locations = split_n_locations

        self.heatmap_nodes = None
        self.result = None

    def run(self):
        """Creates the K-anonymous heatmap based on a Quad-Tree.

        During the execution will transform the original dataset to NumPy for faster processing.
        It will create a GeoPandasFrame (heatmap) and assign it to the self.result variable.
        This new dataset can be obtained with the get_anonymized_dataset method.
        Two tqdm progress bars are used.
        """
        # Transform dataset to NumPy
        logging.info("Transforming dataset to NumPy...")
        np_dataset = self.dataset.to_numpy()

        # Initialize QuadTree with bounding box
        logging.info("Initializing QuadTree...")

        min_x = min(np_dataset[:, 0])
        min_y = min(np_dataset[:, 1])
        max_x = max(np_dataset[:, 0])
        max_y = max(np_dataset[:, 1])
        print((min_x, min_y))
        print((max_x, min_y))
        x_dist = haversine((min_x, min_y), (max_x, min_y), unit=Unit.METERS)
        y_dist = haversine((min_x, min_y), (min_x, max_y), unit=Unit.METERS)
        min_side_dist = min(x_dist, y_dist)
        # min_sector_length = min_side_dist / 2**max_depth
        max_depth = int(math.log(min_side_dist / self.min_sector_length, 2))
        empirical_min_sector_length = min_side_dist / (2**max_depth)
        logging.info(f"QuadTree maximum depth = {max_depth} | "
                     f"Empirical mininum sector length = {empirical_min_sector_length:2f} meters")
        self.qtree = Index(bbox=(min_x, min_y, max_x, max_y),
                           max_items=self.split_n_locations,
                           max_depth=max_depth)

        # Insert locations
        logging.info("Inserting locations to QuadTree...")
        for [x, y] in tqdm(np_dataset[:, :2]):
            # Insert (Object, Bounding box) to QuadTree
            self.qtree.insert((x, y),  # Object
                              (x, y, x, y))  # Bounding box

        # Get QuadTree sectors that have at least min_k locations
        logging.info("Transforming QuadTree to K-anonymous heatmap...")
        self.heatmap_nodes = self.qtree_to_heatmap(self.qtree)

        # Transform heatmap to GeoPandasFrame
        logging.info("Generating GeoPandasFrame...")
        gdf_dict = {"geometry": [], "n_locations": [], "density": []}
        sq_coords_to_sq_mts = partial(pyproj.transform, pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:3857'))   # https://gist.github.com/robinkraft/c6de2f988c9d3f01af3c
        for (bbox, n_locations) in tqdm(self.heatmap_nodes):
            point_list = [[bbox[1], bbox[0]], [bbox[1], bbox[2]], [bbox[3], bbox[2]], [bbox[3], bbox[0]]]
            polygon = geometry.Polygon(point_list)
            gdf_dict["geometry"].append(polygon)
            gdf_dict["n_locations"].append(n_locations)
            area = transform(sq_coords_to_sq_mts, polygon).area  # Transform square coordinates area into square meters
            gdf_dict["density"].append(n_locations/area)
        gdf = GeoDataFrame(gdf_dict)
        self.result = gdf
        logging.info("Heatmap done!")

    def qtree_to_heatmap(self, qtree_elem: _QuadTree) -> list:
        """
        Computes a list of heatmap nodes from the sectors of the QuadTree, always ensuring K-anonymity.

        Parameters
        ----------
        qtree_elem : _QuadTree
            QuadTree to get the sectors (and subsectors) from.

        Returns
        -------
        heatmap : list
            Heatmap nodes as tuples of (bounding box, number of locations)
            See get_bbox documentation for the bounding box format.
        """
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

    def get_bbox(self, qtree_elem: _QuadTree) -> tuple:
        """
        Computes the bounding box of a quadtree sector.

        Parameters
        ----------
        qtree_elem : _QuadTree
            QuadTree sector to get the bounding box from.

        Returns
        -------
        bbox : tuple
            Bounding box of the sector in the form (min_x, min_y, max_x, max_y)
        """
        (center_x, center_y) = qtree_elem.center
        half_width = qtree_elem.width / 2.0
        min_x, max_x = center_x - half_width, center_x + half_width
        half_height = qtree_elem.height / 2.0
        min_y, max_y = center_y - half_height, center_y + half_height
        bbox = (min_x, min_y, max_x, max_y)

        return bbox

    def get_result(self) -> GeoDataFrame:
        """Returns
        -------
        result : GeoDataFrame
            The anonymized heatmap computed at the run method,
            in this case as a GeoPandasFrame with the attributes: geometry (a Polygon), n_locations and density.
        """
        return self.result

    def export_result(self, filepath):
        self.result.to_file(f"{filepath}", driver="GeoJSON")

    @staticmethod
    def get_instance(data, file=None, filetype=None):
        required_fields = ["min_k", "min_sector_length", "merge_sectors", "split_n_locations"]
        values = {}

        for field in required_fields:
            values[field] = data.get(field)
            if values[field] is None:
                logging.info(f"No '{field}' provided. Using {DEFAULT_VALUES[field]}.")
                values[field] = DEFAULT_VALUES[field]

        dataset = Dataset()
        if file is None:
            filename = data.get("input_file")
        else:
            filename = file
        dataset.from_file(filename, filetype, min_locations=1, datetime_key="timestamp")
        dataset.filter_by_speed()

        return QuadTreeHeatMap(dataset, values['min_k'], values["min_sector_length"],
                               values["merge_sectors"], values['split_n_locations'])
