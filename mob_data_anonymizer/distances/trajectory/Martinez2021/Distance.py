import itertools
import logging
from collections import defaultdict
from math import sqrt
from tqdm import tqdm
import random
import sys
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory
from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mob_data_anonymizer.distances.trajectory.DistanceInterface import DistanceInterface


class Distance(DistanceInterface):
    def __init__(self, dataset: Dataset, sp_type='Haversine', landa=None, max_dist=None, normalized=False):
        self.dataset = dataset
        self.spatial_distance = sp_type
        self.distance_matrix = defaultdict(dict)
        self.temporal_matrix = defaultdict(dict)
        self.mean_spatial_distance = 0
        self.mean_temporal_distance = 0
        self.normalized = normalized
        self.average_speed = self.__compute_average_speed()
        self.max_dist = 0  # for normalization [0,1]
        self.reference_trajectory = None
        if landa is None:
            logging.info("Computing weight parameter and max distance")
            self.landa, self.max_dist = self.__set_weight_parameter()   # max_dist for normalization [0,1]
            logging.info(f"\tlanda = {self.landa}")
            logging.info(f"\tmax dist = {self.max_dist}")
            logging.info("Done!")
        else:
            self.landa = landa
            logging.info(f"\tTaking landa = {self.landa}")
            if max_dist is None and normalized:
                logging.info("Computing max distance")  # for normalization [0,1]
                self.max_dist = self.__compute_max_distance()
                logging.info(f"\tmax distance = {self.max_dist}")
            else:
                self.max_dist = max_dist
                logging.info(f"\tTaking max distance = {self.max_dist}")
        self.distance_matrix = defaultdict(dict)
        self.temporal_matrix = defaultdict(dict)

    def __set_weight_parameter(self):
        # if len(self.dataset.trajectories) > 1000:
        #     percen_sample = 10
        #     num_sample = int((len(self.dataset.trajectories) * percen_sample) / 100)
        #     logging.info(f"\tTaking sample for landa = {num_sample} ({percen_sample}%)")
        #     sample = random.sample(self.dataset.trajectories, num_sample)
        # else:
        #     sample = self.dataset.trajectories
        sample = self.dataset.trajectories
        self.distance_matrix = defaultdict(dict)
        self.temporal = defaultdict(dict)
        max_dist = 0
        max_temp = 0
        mean_dist = 0
        mean_temp = 0
        for t1 in tqdm(sample):
            dist = 0
            temp = 0
            for t2 in sample:
                d1 = self.__compute_spatial_distance(t1, t2) * 1000 # meters
                d2 = self.__compute_temporal_distance(t1, t2)   # meters
                if d1 > max_dist:
                    max_dist = d1
                if d2 > max_temp:
                    max_temp = d2
                dist += d1
                temp += d2
            mean_dist += dist / len(sample)
            mean_temp += temp / len(sample)
        mean_dist /= len(sample)
        mean_temp /= len(sample)

        landa = mean_dist / mean_temp
        max_dist = max_dist + (max_temp * landa)
        logging.info(f"mean_dist = {mean_dist}")
        logging.info(f"mean_temp = {mean_temp}")
        logging.info(f"lambda = {landa}")
        logging.info(f"max_dist = {max_dist}")

        return landa, max_dist

    def __compute_average_speed(self):
        logging.info("Computing average speed")
        average_speed = 0
        for traj in tqdm(self.dataset.trajectories):
            average_speed += traj.get_avg_speed()  # km/h
        average_speed /= len(self.dataset.trajectories)
        average_speed /= 3.6  # m/s
        logging.info(f"Average speed: {average_speed} m/s")

        return average_speed

    def __set_weight_parameter_fast(self):
        self.__compute_max_spatial_distance_max_temporal_distance()
        landa = self.mean_spatial_distance / (self.mean_temporal_distance * self.average_speed)

        max_dist = self.mean_spatial_distance + (self.mean_temporal_distance * self.average_speed * landa)

        logging.info(f"mean_dist = {self.mean_spatial_distance}")
        logging.info(f"mean_temp = {self.mean_temporal_distance * self.average_speed}")
        logging.info(f"average_speed = {self.average_speed}")
        logging.info(f"lambda = {landa}")
        logging.info(f"max_dist = {max_dist}")

        return landa, max_dist

    def __compute_max_distance(self):
        self.__compute_max_spatial_distance_max_temporal_distance()
        max_dist = self.mean_spatial_distance + (self.mean_temporal_distance * self.average_speed * self.landa)

        return max_dist

    def __compute_max_spatial_distance_max_temporal_distance(self):
        x_max = float("-inf")
        x_min = float("inf")
        y_max = float("-inf")
        y_min = float("inf")
        t_max = float("-inf")
        t_min = float("inf")
        for traj in tqdm(self.dataset.trajectories):
            for loc in traj.locations:
                if loc.x > x_max:
                    x_max = loc.x
                if loc.x < x_min:
                    x_min = loc.x
                if loc.y > y_max:
                    y_max = loc.y
                if loc.y < y_min:
                    y_min = loc.y
                if loc.timestamp > t_max:
                    t_max = loc.timestamp
                if loc.timestamp < t_min:
                    t_min = loc.timestamp
        l11 = TimestampedLocation(0, x_min, y_min)
        l21 = TimestampedLocation(0, x_max, y_max)
        d1 = l11.spatial_distance(l21) * 1000  # m
        l12 = TimestampedLocation(0, x_max, y_min)
        l22 = TimestampedLocation(0, x_min, y_max)
        d2 = l12.spatial_distance(l22) * 1000  # m
        self.mean_spatial_distance = max(d1, d2) / 2
        self.mean_temporal_distance = (t_max - t_min) / 2

    def compute_reference_trajectory(self):
        x_max = float("-inf")
        x_min = float("inf")
        y_max = float("-inf")
        y_min = float("inf")
        t_max = float("-inf")
        t_min = float("inf")
        for traj in tqdm(self.dataset.trajectories):
            for loc in traj.locations:
                if loc.x > x_max:
                    x_max = loc.x
                if loc.x < x_min:
                    x_min = loc.x
                if loc.y > y_max:
                    y_max = loc.y
                if loc.y < y_min:
                    y_min = loc.y
                if loc.timestamp > t_max:
                    t_max = loc.timestamp
                if loc.timestamp < t_min:
                    t_min = loc.timestamp
        l = TimestampedLocation(t_min, x_min, y_min)
        self.reference_trajectory = Trajectory(0)
        self.reference_trajectory.add_location(l)

    def compute_distance_to_reference_trajectory(self, trajectory):
        return self.compute_without_map(trajectory, self.reference_trajectory)

    def __set_weight_parameter_ant(self):
        # porcen_sample = 50
        # num_sample = int((len(self.dataset.trajectories) * porcen_sample) / 100)
        # logging.info(f"\tTaking sample for landa = {num_sample} ({porcen_sample}%)")
        # sample = random.sample(self.dataset.trajectories, num_sample)
        sample = self.dataset.trajectories
        rsme_dist = 0
        rsme_temp = 0
        for t1 in tqdm(sample):
            dist = 0
            temp = 0
            for t2 in sample:
                d1 = self.__compute_spatial_distance(t1, t2) * 1000 # meters
                d2 = self.__compute_temporal_distance(t1, t2)   # seconds
                dist += pow(d1, 2)
                temp += pow(d2, 2)
            rsme_dist += sqrt(dist) / len(self.dataset.trajectories)
            rsme_temp += sqrt(temp) / len(self.dataset.trajectories)
        rsme_dist /= len(self.dataset.trajectories)
        rsme_temp /= len(self.dataset.trajectories)

        landa = rsme_dist / rsme_temp

        return landa

    def __set_weight_parameter_ant2(self):

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

        logging.debug(f"Max distance: {max_distance} km")
        logging.debug(f"Avg speed: {avg_speed} km/s")
        logging.debug(f"Dif timestamps: {dif_timestamps}")

        return max_distance / (avg_speed * dif_timestamps)

    def compute(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:

        try:
            d = self.distance_matrix[trajectory1.id][trajectory2.id]
            return d
        except KeyError:
            # Distance not computed
            avg_speed_1 = trajectory1.get_avg_speed(sp_type=self.spatial_distance)
            avg_speed_2 = trajectory2.get_avg_speed(sp_type=self.spatial_distance)
            avg_speed = (avg_speed_1 + avg_speed_2) / 2
            avg_speed /= 3.6 # m/s

            h = round((len(trajectory1) + len(trajectory2)) / 2)
            gap_1 = len(trajectory1) / h
            gap_2 = len(trajectory2) / h

            index_1 = index_2 = 0
            i = j = 0

            d = 0

            for k in range(h):

                if i == len(trajectory1):
                    i = len(trajectory1) - 1

                if j == len(trajectory2):
                    j = len(trajectory2) - 1

                loc_1 = trajectory1.locations[i]
                loc_2 = trajectory2.locations[j]

                d1 = loc_1.spatial_distance(loc_2, type=self.spatial_distance) * 1000   # meters
                d2 = self.landa * (loc_1.temporal_distance(loc_2)) * avg_speed  # meters
                d += pow(d1 + d2, 2)

                index_1 += gap_1
                index_2 += gap_2

                i = round(index_1)
                j = round(index_2)

            d /= h

            d = sqrt(d)

            if self.normalized:
                d /= self.max_dist  # normalization [0,1]

        # Store the distance for later use
        self.distance_matrix[trajectory1.id][trajectory2.id] = d
        self.distance_matrix[trajectory2.id][trajectory1.id] = d

        return d

    def compute_without_map(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        avg_speed_1 = trajectory1.get_avg_speed(sp_type=self.spatial_distance)
        avg_speed_2 = trajectory2.get_avg_speed(sp_type=self.spatial_distance)
        avg_speed = (avg_speed_1 + avg_speed_2) / 2
        avg_speed /= 3.6  # m/s

        h = round((len(trajectory1) + len(trajectory2)) / 2)
        gap_1 = len(trajectory1) / h
        gap_2 = len(trajectory2) / h

        index_1 = index_2 = 0
        i = j = 0

        d = 0

        for k in range(h):

            if i == len(trajectory1):
                i = len(trajectory1) - 1

            if j == len(trajectory2):
                j = len(trajectory2) - 1

            loc_1 = trajectory1.locations[i]
            loc_2 = trajectory2.locations[j]

            d1 = loc_1.spatial_distance(loc_2, type=self.spatial_distance) * 1000  # meters
            d2 = self.landa * (loc_1.temporal_distance(loc_2)) * avg_speed  # meters
            d += pow(d1 + d2, 2)

            index_1 += gap_1
            index_2 += gap_2

            i = round(index_1)
            j = round(index_2)

        d /= h

        d = sqrt(d)

        if self.normalized:
            d /= self.max_dist  # normalization [0,1]

        return d

    def __compute_spatial_distance(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        try:
            d = self.distance_matrix[trajectory1.id][trajectory2.id]
            return d
        except KeyError:
            # Distance not computed
            h = round((len(trajectory1) + len(trajectory2)) / 2)
            gap_1 = len(trajectory1) / h
            gap_2 = len(trajectory2) / h

            index_1 = index_2 = 0
            i = j = 0

            d = 0

            for k in range(h):

                if i == len(trajectory1):
                    i = len(trajectory1) - 1

                if j == len(trajectory2):
                    j = len(trajectory2) - 1

                loc_1 = trajectory1.locations[i]
                loc_2 = trajectory2.locations[j]

                d += pow(loc_1.spatial_distance(loc_2, type=self.spatial_distance), 2)

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

    def __compute_temporal_distance(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        try:
            d = self.temporal_matrix[trajectory1.id][trajectory2.id]
            return d
        except KeyError:
        # Distance not computed
            avg_speed_1 = trajectory1.get_avg_speed(sp_type=self.spatial_distance)
            avg_speed_2 = trajectory2.get_avg_speed(sp_type=self.spatial_distance)
            avg_speed = (avg_speed_1 + avg_speed_2) / 2

            h = round((len(trajectory1) + len(trajectory2)) / 2)
            gap_1 = len(trajectory1) / h
            gap_2 = len(trajectory2) / h

            index_1 = index_2 = 0
            i = j = 0

            d = 0

            for k in range(h):

                if i == len(trajectory1):
                    i = len(trajectory1) - 1

                if j == len(trajectory2):
                    j = len(trajectory2) - 1

                loc_1 = trajectory1.locations[i]
                loc_2 = trajectory2.locations[j]

                d += pow(loc_1.temporal_distance(loc_2) * avg_speed, 2)

                index_1 += gap_1
                index_2 += gap_2

                i = round(index_1)
                j = round(index_2)

            d /= h

            d = sqrt(d)

        # Store the distance for later use
        self.temporal_matrix[trajectory1.id][trajectory2.id] = d
        self.temporal_matrix[trajectory2.id][trajectory1.id] = d

        return d

    def filter_dataset(self):
        return self.dataset
