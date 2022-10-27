from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.pyqtree import Index
import logging
from tqdm import tqdm
from shapely import geometry
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt

DEFAULT_VALUES = {
    "min_k": 5,
    "max_locations": 10,
    "max_depth": 30
}


class QuadTreeHeatMap:
    """Creates a heatmap of the data via a QuadTree (Klinger, A., & Dyer, C. R. 1976, https://www.sciencedirect.com/science/article/abs/pii/S0146664X76800068).
    Similar approach to the used in https://www.idescat.cat/sort/sort411/41.1.7.lagonigro-etal.prov.pdf
    """

    def __init__(self, dataset: Dataset, min_k: int, max_locations: int, max_depth: int):
        """
        Parameters
        ----------
        dataset : Dataset
            Dataset to anonymize.
        min_k : int
            Minimum number of locations allowed co-exist in a QuadTree sector.
        max_locations : int
            Maximum number of locations allowed in a QuadTree sector before it is split.
        max_depth : int
            Maximum depth allowed for the QuadTree.
        """
        self.dataset = dataset
        self.min_k = min_k
        self.max_locations = max_locations
        self.max_depth = max_depth
        self.heatmap_nodes = []

        self.anonymized_dataset = dataset.__class__()

    def run(self):
        # Reset heatmap and transform dataset to NumPy
        self.heatmap_nodes = []
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
        for location in tqdm(np_dataset[:, :2]):
            [x, y] = location
            # Insert (Object, Bounding box) to QuadTree
            self.qtree.insert((x, y),  # Object
                              (x, y, x, y))  # Bounding box

        # Get QuadTree sectors that have at least min_k locations
        logging.info("Generalizing with QuadTree...")
        self.heatmap_nodes = self.qtree_to_heatmap(self.qtree)
        logging.info("Done!")

        # Transform heatmap to GeoPandasFrame
        idx = 0
        gdf_dict = {"geometry": [], "n_location": []}
        for (bbox, n_locations) in self.heatmap_nodes:
            point_list = [[bbox[0], bbox[1]], [bbox[2], bbox[1]], [bbox[2], bbox[3]], [bbox[0], bbox[3]]]
            polygon = geometry.Polygon(point_list)
            gdf_dict["geometry"].append(polygon)
            gdf_dict["n_location"].append(n_locations)
        gdf = GeoDataFrame(gdf_dict)
        self.anonymized_dataset = gdf

        # Plotting # TODO: Remove
        fig, ax = plt.subplots(1, 1)
        gdf.plot(column='n_location', cmap='OrRd', ax=ax, legend=True)
        bdf = GeoDataFrame(geometry=gdf.boundary)
        bdf.plot()
        plt.show()


    def qtree_to_heatmap(self, qtree_elem):
        heatmap = []
        # If no children, add *parent* to heatmap
        if len(qtree_elem.children) == 0:
            n_parent_locations = len(qtree_elem)
            heatmap.append((self.get_bbox(qtree_elem), n_parent_locations))
        # Otherwise, check children
        else:
            for child in qtree_elem.children:
                n_child_locations = len(child)
                # If not enough locations, ONLY add *parent* to heatmap and break
                if n_child_locations < self.min_k:
                    n_parent_locations = len(qtree_elem)
                    heatmap = [] # Reset heatmap of nodes from other children
                    heatmap = [(self.get_bbox(qtree_elem), n_parent_locations)]  # Add parent
                    break
                # Otherwise, has enough locations, search inside
                else:
                    heatmap += self.qtree_to_heatmap(child)

        return heatmap

    def get_bbox(self, qtree_elem):
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
        required_fields = ["min_k", "max_locations", "max_depth"]
        values = {}

        for field in required_fields:
            values[field] = data.get(field)
            if not values[field]:
                logging.info(f"No '{field}' provided. Using {DEFAULT_VALUES[field]}.")
                values[field] = DEFAULT_VALUES[field]

        dataset = Dataset()
        dataset.load_from_scikit(data.get("input_file"), min_locations=5, datetime_key="timestamp")
        dataset.filter_by_speed()

        return QuadTreeHeatMap(dataset, values['min_k'],
                               values['max_locations'], values["max_depth"])
