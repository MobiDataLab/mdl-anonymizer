from mob_data_anonymizer.measures_methods.MeasuresMethodInterface import MeasuresMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from collections import defaultdict
from math import sqrt
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
    
}


class Rsme(MeasuresMethodInterface):
    def __init__(self, original_dataset: Dataset, anom_dataset: Dataset, trajectory_distance):
        self.original_dataset = original_dataset
        self.anom_dataset = anom_dataset
        self.trajectory_distance = trajectory_distance
        self.results = {}

    def run(self):
        self.results["rsme"] = round(self.get_rsme(self.trajectory_distance), 4)
        logging.info(f'RSME: {self.results["rsme"]}')

    def get_result(self):
        return self.results

    def get_rsme(self, distance):
        # TODO: Y como se mide la diferencia cuando una trayectoría ha sido eliminada?
        distance.distance_matrix = defaultdict(dict)
        anom_trajectories = {}
        for t in self.anom_dataset.trajectories:
            anom_trajectories[t.id] = t
        dist = 0.0
        for t_ori in self.original_dataset.trajectories:
            if t_ori.id in anom_trajectories:
                t_anon = anom_trajectories[t_ori.id]
                d = distance.compute(t_ori, t_anon)
                dist += pow(d, 2)
        dist /= len(self.anom_dataset)
        dist = sqrt(dist)

        return dist
