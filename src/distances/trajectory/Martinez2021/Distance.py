import itertools
from collections import defaultdict
from math import sqrt

from src.entities.Dataset import Dataset
from src.entities.Trajectory import Trajectory
from src.distances.trajectory.DistanceInterface import DistanceInterface


class Distance(DistanceInterface):

    def __init__(self, dataset: Dataset, sp_type='Haversine'):
        self.dataset = dataset
        self.spatial_distance = sp_type
        self.distance_matrix = defaultdict(dict)

        self.landa = self.__set_weight_parameter()

    def __set_weight_parameter(self):
        # We need the maximum distance between points in the data set, maximum time difference between points in
        # the data set and the avg velocity of the trajectories in the data set
        avg_speed = 0.0
        min_timestamp = 9213084687
        max_timestamp = 0

        for i, t in enumerate(self.dataset.trajectories):
            # Speed
            avg_speed += t.get_avg_speed(unit='kms', sp_type=self.spatial_distance)

            # Timestamp
            if t.get_first_timestamp() < min_timestamp:
                min_timestamp = t.get_first_timestamp()

            if t.get_last_timestamp() > max_timestamp:
                max_timestamp = t.get_last_timestamp()

        dif_timestamps = max_timestamp - min_timestamp
        avg_speed /= len(self.dataset)

        # Max distance
        max_distance = 0
        for t1, t2 in itertools.combinations(self.dataset.trajectories, 2):
            for l1 in t1.locations:
                for l2 in t2.locations:
                    d = l1.spatial_distance(l2, type=self.spatial_distance)
                    if d > max_distance:
                        max_distance = d

        return max_distance / (avg_speed * dif_timestamps)

    def compute(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:

        try:
            d = self.distance_matrix[trajectory1.id][trajectory2.id]
        except KeyError:
            # Distance not computed
            h = round((len(trajectory1) + len(trajectory2)) / 2)
            gap_1 = len(trajectory1) / h
            gap_2 = len(trajectory2) / h

            index_1 = index_2 = 0
            i = j = 0

            d = 0

            for k in range(h):
                loc_1 = trajectory1.locations[i]
                loc_2 = trajectory2.locations[j]

                avg_speed_1 = trajectory1.get_avg_speed(sp_type=self.spatial_distance)
                avg_speed_2 = trajectory2.get_avg_speed(sp_type=self.spatial_distance)
                avg_speed = (avg_speed_1 + avg_speed_2) / 2

                d += (loc_1.spatial_distance(loc_2, type=self.spatial_distance) +
                             self.landa * (loc_1.temporal_distance(loc_2)) * avg_speed)

                index_1 += gap_1
                index_2 += gap_2

                i = round(index_1)
                j = round(index_2)

            d /= h

            d = sqrt(d)

        # Store the distance for later use
        self.distance_matrix[trajectory1.id][trajectory2.id] = d
        self.distance_matrix[trajectory2.id][trajectory1.id] = d

        return d
