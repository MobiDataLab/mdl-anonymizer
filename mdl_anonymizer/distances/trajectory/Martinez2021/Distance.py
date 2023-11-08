import itertools
import logging
from collections import defaultdict
from math import sqrt
from tqdm import tqdm
import math
import random
import sys
from mdl_anonymizer.entities.Dataset import Dataset
from mdl_anonymizer.entities.Trajectory import Trajectory
from mdl_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mdl_anonymizer.distances.trajectory.DistanceInterface import DistanceInterface
from mdl_anonymizer.utils.utils import memory


class Distance(DistanceInterface):
    def __init__(self, dataset: Dataset, sp_type='Haversine', p_lambda=None, max_dist=None, normalized=False, checking=False):
        self.dataset = dataset
        self.spatial_distance = sp_type
        self.distance_matrix = {}
        self.temporal_matrix = {}
        self.mean_spatial_distance = 0
        self.mean_temporal_distance = 0
        self.normalized = normalized

        # Don't compute anything If we are just checking if an object can be instantiated
        if checking:
            return

        self.average_speed = self.__compute_average_speed()
        self.max_dist = 0  # for normalization [0,1]
        self.reference_trajectory = None
        available_mem = memory()
        needed_mem = (pow(len(self.dataset.trajectories), 2) * 12) / (1024 * 1024)
        if available_mem > needed_mem:
            self.compute = self.compute_no_memory_control
            logging.info(f"Computing distances without memory control. ")
                         # f"Available: {available_mem}, Needed: {needed_mem}")
        else:
            self.compute = self.compute_with_memory_control
            logging.info(f"Computing distances with memory control. ")
                         # f"Available: {available_mem}, Needed: {needed_mem}")
        if p_lambda is None:
            logging.info("Computing weight parameter and max distance")
            self.p_lambda, self.max_dist = self.__set_weight_parameter()   # max_dist for normalization [0,1]
            logging.info(f"\tlambda = {self.p_lambda}")
            logging.info(f"\tmax dist = {self.max_dist}")
            logging.info("Done!")
        else:
            self.p_lambda = p_lambda
            logging.info(f"\tTaking lambda = {self.p_lambda}")
            if max_dist is None and normalized:
                logging.info("Computing max distance")  # for normalization [0,1]
                self.max_dist = self.__compute_max_distance()
                logging.info(f"\tmax distance = {self.max_dist}")
            else:
                self.max_dist = max_dist
                logging.info(f"\tTaking max distance = {self.max_dist}")
        self.distance_matrix = {}
        self.temporal_matrix = {}

    def compute(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        pass

    def __set_weight_parameter(self):
        if len(self.dataset.trajectories) > 10000:
            num_sample = self.calculate_sample_size()
            sample = random.sample(self.dataset.trajectories, num_sample)
        else:
            num_sample = len(self.dataset.trajectories)
            sample = self.dataset.trajectories
        logging.info(f"\tTaking sample for lambda = {num_sample})")

        # num_sample = len(self.dataset.trajectories)
        # percen_sample = 100
        # if len(self.dataset.trajectories) > 10000:
        #     percen_sample = 10
        # if len(self.dataset.trajectories) > 100000:
        #     percen_sample = 1
        # if len(self.dataset.trajectories) > 1000000:
        #     percen_sample = 0.1
        # if percen_sample < 100:
        #     num_sample = int((len(self.dataset.trajectories) * percen_sample) / 100)
        #     sample = random.sample(self.dataset.trajectories, num_sample)
        # logging.info(f"\tTaking sample for lambda = {num_sample} ({percen_sample}%)")
        # sample = self.dataset.trajectories
        self.distance_matrix = {}
        self.temporal_matrix = {}
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

    def calculate_sample_size2(self):
        size = len(self.dataset.trajectories)
        magnitude = math.floor(math.log10(size))
        percen = 100 / (pow(10, magnitude) / 1000)
        num_sample = int((size * percen) / 100)

        return num_sample

    def calculate_sample_size(self):
        '''
        https://www.wikihow.com/Calculate-Sample-Size
        '''
        # z_score = 1.96   # 95% confidence
        # z_score = 1.645  # 90% confidence
        z_score = 2.576  # 99% confidence
        error = 0.03    # 3%
        sd = 0.5    # expected standard deviation
        size = len(self.dataset.trajectories)

        sample = (pow(z_score, 2)*(sd*(1-sd)))/(pow(error, 2)) / \
                 (1+((pow(z_score, 2)*(sd*(1-sd)))/(pow(error, 2) * size)))

        return int(sample)

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
        p_lambda = self.mean_spatial_distance / (self.mean_temporal_distance * self.average_speed)

        max_dist = self.mean_spatial_distance + (self.mean_temporal_distance * self.average_speed * p_lambda)

        logging.info(f"mean_dist = {self.mean_spatial_distance}")
        logging.info(f"mean_temp = {self.mean_temporal_distance * self.average_speed}")
        logging.info(f"average_speed = {self.average_speed}")
        logging.info(f"lambda = {p_lambda}")
        logging.info(f"max_dist = {max_dist}")

        return p_lambda, max_dist

    def __compute_max_distance(self):
        self.__compute_max_spatial_distance_max_temporal_distance()
        max_dist = self.mean_spatial_distance + (self.mean_temporal_distance * self.average_speed * self.p_lambda)

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

    def compute_no_memory_control(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        key = trajectory1.str_id + "-" + trajectory2.str_id
        d = self.distance_matrix.get(key)
        if d is not None:
            return d
        key = trajectory2.str_id + "-" + trajectory1.str_id
        d = self.distance_matrix.get(key)
        if d is not None:
            return d
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
            d2 = self.p_lambda * (loc_1.temporal_distance(loc_2)) * avg_speed  # meters
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
        self.distance_matrix[key] = d

        return d

    def compute_with_memory_control(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        key = trajectory1.str_id + "-" + trajectory2.str_id
        d = self.distance_matrix.get(key)
        if d is not None:
            return d
        key = trajectory2.str_id + "-" + trajectory1.str_id
        d = self.distance_matrix.get(key)
        if d is not None:
            return d
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
            d2 = self.p_lambda * (loc_1.temporal_distance(loc_2)) * avg_speed  # meters
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
        if memory() < 1000:  #MB
            print("Memory low, cleaning memory")
            self.distance_matrix = {}
        self.distance_matrix[key] = d

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
            d2 = self.p_lambda * (loc_1.temporal_distance(loc_2)) * avg_speed  # meters
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
        key = trajectory1.str_id + "-" + trajectory2.str_id
        d = self.distance_matrix.get(key)
        if d is not None:
            return d
        key = trajectory2.str_id + "-" + trajectory1.str_id
        d = self.distance_matrix.get(key)
        if d is not None:
            return d

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
        self.distance_matrix[key] = d

        return d

    def __compute_temporal_distance(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        key = trajectory1.str_id + "-" + trajectory2.str_id
        d = self.temporal_matrix.get(key)
        if d is not None:
            return d
        key = trajectory2.str_id + "-" + trajectory1.str_id
        d = self.temporal_matrix.get(key)
        if d is not None:
            return d

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
        self.temporal_matrix[key] = d

        return d

    def filter_dataset(self):
        return self.dataset

    def clear_memory(self):
        self.distance_matrix = {}
        self.temporal_matrix = {}