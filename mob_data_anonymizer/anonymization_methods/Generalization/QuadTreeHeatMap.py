from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.pyqtree import Index
import logging
from tqdm import tqdm

DEFAULT_VALUES = {
    "min_k": 3,
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
        for location in tqdm(np_dataset):
            [x, y, timestamp, id] = location
            self.qtree.insert((x, y), (x, y, x, y)) # Args = Element, BoundingBox

        # Get QuadTree sectors that have at least min_k locations
        logging.info("Generalizing with QuadTree...")
        self.qtree_to_heatmap(self.qtree, self.heatmap_nodes)
        logging.info("Done!")

        return self.heatmap_nodes

    def qtree_to_heatmap(self, qtree_elem, heatmap: list):
        for child in qtree_elem.children:
            # If not enough locations add *parent* to heatmap
            n_child_locations = len(child)
            if n_child_locations < self.min_k:
                n_parent_locations = len(qtree_elem)
                heatmap.append((self.get_bbox(qtree_elem), n_parent_locations))
            # Otherwise, has enough locations
            else:
                # If no grandchildren, add *child* to heatmap
                if len(child.children) == 0:
                    heatmap.append((self.get_bbox(child), n_child_locations))
                # Otherwise, search in the grandchildren
                else:
                    self.qtree_to_heatmap(child, heatmap)

    def get_bbox(self, qtree_elem):
        (center_x, center_y) = qtree_elem.center
        half_width = qtree_elem.width / 2.0
        min_x, max_x = center_x - half_width, center_x + half_width
        half_height = qtree_elem.height / 2.0
        min_y, max_y = center_y - half_height, center_y + half_height
        bbox = (min_x, min_y, max_x, max_y)
        return bbox
