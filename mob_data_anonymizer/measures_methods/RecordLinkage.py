from mob_data_anonymizer.measures_methods.MeasuresMethodInterface import MeasuresMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from bisect import bisect_left
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
import random
from datetime import datetime

DEFAULT_VALUES = {

}


class RecordLinkage(MeasuresMethodInterface):
    def __init__(self, original_dataset: Dataset, anom_dataset: Dataset, trajectory_distance, percen_window_size=None,
                 seed: int = None):
        self.original_dataset = original_dataset
        self.anom_dataset = anom_dataset
        self.trajectory_distance = trajectory_distance
        self.percen_window_size = percen_window_size
        self.results = {}
        self.seed = seed

    def run(self):

        # Set seed
        if self.seed is not None:
            random.seed(self.seed)

        self.results["percen_record_linkage"] = round(self.get_fast_record_linkage(self.trajectory_distance), 2)
        # print(f'% Record linkage: {self.results["percen_record_linkage"]}')

        self.results["percen_record_linkage_sample"] = round(self.get_sample_record_linkage(self.trajectory_distance), 2)
        # print(f'% Record linkage: {self.results["percen_record_linkage_sample"]}')

    def get_result(self):
        return self.results

    def get_fast_record_linkage(self, distance):
        if self.percen_window_size is None:
            window_size = self.calculate_window_size()
        else:
            window_size = (len(self.original_dataset) * self.percen_window_size) / 100

        logging.info("Calculating fast record linkage (disclosure risk), window size = " + str(window_size))
        distance.compute_reference_trajectory()

        control = {}
        ids = {}
        for trajectory in self.original_dataset.trajectories:
            trajectory.distance_to_reference_trajectory = \
                distance.compute_distance_to_reference_trajectory(trajectory)
            count = control.get(trajectory)
            if count is not None:
                count += 1
            else:
                count = 1
                ids[trajectory] = []
            control[trajectory] = count
            ids[trajectory].append(trajectory.id)

        self.original_dataset.trajectories.sort(key=lambda x: x.distance_to_reference_trajectory)
        distances = [trajectory.distance_to_reference_trajectory for trajectory in self.original_dataset.trajectories]
        min_traj = None
        total_prob = 0
        for trajectory_anom in tqdm(self.anom_dataset.trajectories):
            trajectory_anom.distance_to_reference_trajectory = \
                distance.compute_distance_to_reference_trajectory(trajectory_anom)
            closest_trajectories = RecordLinkage.__take_closest_window(distances,
                                                                       trajectory_anom.distance_to_reference_trajectory,
                                                                       window_size)
            min_dist = float('inf')
            for pos in closest_trajectories:
                trajectory = self.original_dataset.trajectories[pos]
                dist = distance.compute_without_map(trajectory, trajectory_anom)
                if dist < min_dist:
                    min_dist = dist
                    min_traj = trajectory
            ids_group = ids[min_traj]
            if trajectory_anom.id in ids_group:
                count = control[min_traj]
                partial = 1 / count
                total_prob += partial

        # rearranging
        self.original_dataset.trajectories.sort(key=lambda x: x.id)

        return (total_prob / len(self.original_dataset)) * 100

    def __take_closest(myList, myNumber):
        """
        Assumes myList is sorted. Returns the index of the closest value to myNumber.
        If two numbers are equally close, return the index of the smallest number.
        :param (list) myList: the list of values
        :param (float) myNumber: The number to be searched
        :return: The index of myList of the closest value to myNumber
        :rtype: int
        """
        pos = bisect_left(myList, myNumber)
        if pos == 0:
            return pos
            # return myList[0]
        if pos == len(myList):
            return pos
            # return m/yList[-1]
        before = myList[pos - 1]
        after = myList[pos]
        if after - myNumber < myNumber - before:
            # return after
            return pos
        else:
            # return before
            return pos - 1

    def __take_closest_window(myList, myNumber, window_size):
        """
        Assumes myList is sorted. Returns a list of positions of my list with size window_size.
        The window_size positions of the closest values in mylist to myNumber.
        :param (list) myList: the list of values
        :param (float) myNumber: The number to be searched
        :param (float) window_size: The number of positions to be returned
        :return: The list of indexes of myList of the closest value to myNumber
        :rtype: list of int
        """

        pos = RecordLinkage.__take_closest(myList, myNumber)
        cut = int(window_size / 2)
        rest_before = 0
        rest_after = 0
        pos_before = pos - cut
        if window_size % 2 == 0:
            pos_before += 1
        if pos_before < 0:
            rest_before = pos_before * -1
            pos_before = 0
        pos_after = pos + cut
        if pos_after > len(myList) - 1:
            rest_after = pos_after - (len(myList) - 1)
            pos_after = len(myList) - 1
        pos_before -= rest_after
        pos_after += rest_before

        return [x for x in range(pos_before, pos_after + 1)]

    def calculate_window_size(self):
        size = len(self.original_dataset.trajectories)
        if size < 100:
            return size

        magnitude = math.floor(math.log10(size))
        percen = 100 / (pow(10, magnitude) / 100)
        window_size = int((size * percen) / 100)

        return window_size

    def get_sample_record_linkage(self, distance):
        logging.info("Calculating privacy metric (sample record linkage)")
        if len(self.original_dataset.trajectories) > 11000:
            num_sample = self.calculate_sample_size()
            seed = datetime.now()
            random.seed(seed)
            sample_original = random.sample(self.original_dataset.trajectories, num_sample)
            sample_anom = []
            anom_trajectories = {}
            for t in self.anom_dataset.trajectories:
                anom_trajectories[t.id] = t
            for t_ori in sample_original:
                if t_ori.id in anom_trajectories:
                    t_anon = anom_trajectories[t_ori.id]
                    sample_anom.append(t_anon)
            # random.seed(seed)
            # sample_anom = random.sample(self.anom_dataset.trajectories, num_sample)
        else:
            num_sample = len(self.original_dataset.trajectories)
            sample_original = self.original_dataset.trajectories
            sample_anom = self.anom_dataset.trajectories
        logging.info(f"\tTaking sample for record linkage = {num_sample})")
        control = {}
        ids = {}
        for trajectory in sample_original:
            count = control.get(trajectory)
            if count is not None:
                count += 1
            else:
                count = 1
                ids[trajectory] = []
            control[trajectory] = count
            ids[trajectory].append(trajectory.id)

        total_prob = 0
        min_traj = None
        for traj_anom in tqdm(sample_anom):
            min_dist = float('inf')
            for traj_ori in sample_original:
                dist = distance.compute_without_map(traj_ori, traj_anom)
                if dist < min_dist:
                    min_dist = dist
                    min_traj = traj_ori
            ids_group = ids[min_traj]
            if traj_anom.id in ids_group:
                count = control[min_traj]
                partial = 1 / count
                total_prob += partial

        # # extrapolate
        # total_prob = (total_prob * len(self.original_dataset)) / len(sample_original)

        return (total_prob / len(sample_original)) * 100

    def calculate_sample_size(self):
        '''
        https://www.wikihow.com/Calculate-Sample-Size
        '''
        # z_score = 1.96   # 95% confidence
        # z_score = 1.645  # 90% confidence
        z_score = 2.576  # 99% confidence
        error = 0.03    # 3%
        sd = 0.5    # expected standard deviation
        size = len(self.original_dataset.trajectories)

        sample = (pow(z_score, 2)*(sd*(1-sd)))/(pow(error, 2)) / \
                 (1+((pow(z_score, 2)*(sd*(1-sd)))/(pow(error, 2) * size)))

        return int(sample)

    def get_record_linkage(self, distance):
        logging.info("Calculating privacy metric (record linkage)")
        control = {}
        ids = {}
        for trajectory in self.original_dataset.trajectories:
            count = control.get(trajectory)
            if count is not None:
                count += 1
            else:
                count = 1
                ids[trajectory] = []
            control[trajectory] = count
            ids[trajectory].append(trajectory.id)

        total_prob = 0
        min_traj = None
        for traj_anom in tqdm(self.anom_dataset.trajectories):
            min_dist = float('inf')
            for traj_ori in self.original_dataset.trajectories:
                dist = distance.compute_without_map(traj_ori, traj_anom)
                if dist < min_dist:
                    min_dist = dist
                    min_traj = traj_ori
            ids_group = ids[min_traj]
            if traj_anom.id in ids_group:
                count = control[min_traj]
                partial = 1 / count
                total_prob += partial

        # # extrapolate
        # total_prob = (total_prob * len(self.original_dataset)) / len(sample_original)

        return (total_prob / len(self.original_dataset.trajectories)) * 100
