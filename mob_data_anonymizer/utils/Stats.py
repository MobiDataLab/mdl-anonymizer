from collections import defaultdict
from math import sqrt
import logging
from tqdm import tqdm
from mob_data_anonymizer.entities.Dataset import Dataset
from bisect import bisect_left


class Stats:

    def __init__(self, original: Dataset, anonymized: Dataset):
        self.original_dataset = original
        self.anonymized_dataset = anonymized

    def get_number_of_removed_trajectories(self):
        return len(self.original_dataset) - len(self.anonymized_dataset)

    def get_number_of_removed_locations(self):
        return self.original_dataset.get_number_of_locations() - self.anonymized_dataset.get_number_of_locations()

    def get_perc_of_removed_trajectories(self):
        return self.get_number_of_removed_trajectories() / len(self.original_dataset)

    def get_perc_of_removed_locations(self):
        return self.get_number_of_removed_locations() / self.original_dataset.get_number_of_locations()

    def get_rsme(self, distance):
        # TODO: Y como se mide la diferencia cuando una trayectoría ha sido eliminada?
        dist = 0.0
        for t1 in self.original_dataset.trajectories:
            t1_anon = self.anonymized_dataset.get_trajectory(t1.id)
            if t1_anon:
                d = distance.compute(t1, t1_anon)
                if d and d != 9999999999999:
                    dist += pow(d, 2)
        dist /= len(self.anonymized_dataset)
        dist = sqrt(dist)

        return dist

    def get_rsme_ordered(self, distance):
        # TODO: Y como se mide la diferencia cuando una trayectoría ha sido eliminada?
        distance.distance_matrix = defaultdict(dict)
        dist = 0.0
        dist2 = 0
        for i, t1 in enumerate(self.original_dataset.trajectories):
            t1_anon = self.anonymized_dataset.trajectories[i]
            if t1_anon:
                d = distance.compute(t1, t1_anon)
                if d and d != 9999999999999:
                    dist += pow(d, 2)
        dist /= len(self.anonymized_dataset)
        dist = sqrt(dist)

        return dist

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
        for traj_anom in tqdm(self.anonymized_dataset.trajectories):
            min_dist = float('inf')
            for traj_ori in self.original_dataset.trajectories:
                dist = distance.compute(traj_ori, traj_anom)
                if dist < min_dist:
                    min_dist = dist
                    min_traj = traj_ori
            ids_group = ids[min_traj]
            if traj_anom.id in ids_group:
                count = control[min_traj]
                partial = 1 / count
                total_prob += partial

        return (total_prob / len(self.original_dataset)) * 100

    def get_fast_record_linkage(self, distance, window_size = None):
        WINDOW_SIZE = 1 # it indicates the % of the num of trajectories in the dataset
        if window_size is None:
            window_size = (len(self.original_dataset) * WINDOW_SIZE) / 100
            if window_size < 1.0:
                window_size = len(self.original_dataset)
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
        for trajectory_anom in tqdm(self.anonymized_dataset.trajectories):
            closest_trajectories = Stats.take_closest_window(distances,
                                                             trajectory_anom.distance_to_reference_trajectory,
                                                             window_size)
            min_dist = float('inf')
            for pos in closest_trajectories:
                trajectory = self.original_dataset.trajectories[pos]
                dist = distance.compute(trajectory, trajectory_anom)
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

    def take_closest(myList, myNumber):
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

    def take_closest_window(myList, myNumber, window_size):
        """
        Assumes myList is sorted. Returns a list of positions of my list with size window_size.
        The window_size positions of the closest values in mylist to myNumber.
        :param (list) myList: the list of values
        :param (float) myNumber: The number to be searched
        :param (float) window_size: The number of positions to be returned
        :return: The list of indexes of myList of the closest value to myNumber
        :rtype: list of int
        """
        pos = Stats.take_closest(myList, myNumber)
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