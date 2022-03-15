import logging
import random
import numpy as np
from tqdm import tqdm

from src.entities.Dataset import Dataset
from src.entities.Trajectory import Trajectory
from src.entities.TimestampedLocation import TimestampedLocation


class SwapMob:
    def __init__(self, dataset: Dataset, spatial_thold, temporal_thold):
        self.dataset = dataset
        self.spatial_thold = spatial_thold
        self.temporal_thold = temporal_thold

        self.anonymized_dataset = dataset.__class__()

    def run(self):
        # Get the original dataset as NumPy array sort by timestamp
        np_dataset = self.dataset.to_numpy(sort_by_timestamp=True)

        # Get first and last timestamp of the dataset
        first_timestamp, last_timestamp = self.get_first_and_last_timestamps(np_dataset)

        # Swap trajectories
        logging.info("Swapping...")
        num_intervals = (last_timestamp - first_timestamp - 1) // self.temporal_thold + 1
        last_end_idx = 0
        for i in tqdm(range(num_intervals), desc="Num. time intervals"):
            # Get initial and final timestamps of the interval
            ini_t = first_timestamp + i * self.temporal_thold
            end_t = min(ini_t + self.temporal_thold, last_timestamp)

            # Get locations in the interval
            locs_in_interval, ini_idx, end_idx = self.get_locations_in_interval(np_dataset, ini_t, end_t, last_end_idx)

            # Get possible swaps depending on the distance
            possible_swaps = self.get_possible_swaps(locs_in_interval)

            # TODO: Get selection of swaps


            # TODO: Perform swaps


            # Update last_end_idx for next interval computation
            last_end_idx = end_idx

        logging.info("Swapping done!")

        # Transform np_dataset to anonymized dataset
        self.anonymized_dataset.from_numpy(np_dataset)

        # Remove trajectories with less than 1 locations
        logging.info("Remove trajectories with less than 1 locations")
        self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]

        # Remove trajectories without swaps
        logging.info("Remove trajectories without swaps")
        # self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]  # TODO

        logging.info("Done!")


    def get_first_and_last_timestamps(self, np_dataset):
        """CAUTION: It assumes that np_dataset is sorted by timestamp"""
        first_timestamp = np_dataset[0][2]
        last_timestamp = np_dataset[-1][2]
        return first_timestamp, last_timestamp


    def get_locations_in_interval(self, np_dataset, ini_t, end_t, last_end_idx=0):
        """Get locations existing in the time interval [ini_t, end_t]
        last_end_idx is the end_idx of the last call (used for avoiding re-computation)
        CAUTION: It assumes that np_dataset is sorted by timestamp"""
        # Get only the dataset from the last for avoiding re-computation
        considered_dataset = np_dataset[last_end_idx:]

        # Get ini and end indeces of locations in interval (np_dataset SORTED BY TIMESTAMP IS ASSUMED)
        ini_idx = np.argmax(considered_dataset >= ini_t)    # ArgMax gets the first index where condition is true
        end_idx = np.argmax(considered_dataset[ini_idx+1:] > end_t)     # ArgMax gets the first index where condition is true

        # Adjust ini and end indeces to real positions
        ini_idx += last_end_idx
        end_idx += ini_idx+1    # Used for avoiding future re-computation (next last_end_idx)

        # Get locations in time interval
        locs_in_interval = np_dataset[ini_idx:end_idx]

        return locs_in_interval, ini_idx, end_idx


    def get_possible_swaps(self, locs_in_interval):
        # Transform array elements to locations
        locations = []
        for loc in locs_in_interval:
            locations.append(TimestampedLocation(loc[2], loc[0], loc[1]))

        # Get possible swaps
        possible_swaps = []
        for idx1, l1 in enumerate(locations):
            if idx1 < len(locations) - 1:
                for idx2, l2 in enumerate(locations[idx1 + 1:]):
                    if l1.spatial_distance(l2) < self.spatial_thold:
                        possible_swaps.append((idx1, idx2))

        return possible_swaps

    def run_old(self):
        # Create anonymized dataset as a copy of the original dataset
        for t in self.dataset.trajectories:
            self.anonymized_dataset.add_trajectory(
                Trajectory(t.id))  # TODO: Since I change trajectories, this must be an object copy
        logging.info("Anonymized dataset initialized!")

        # Get first and last timestamp of the dataset
        first_timestamp, last_timestamp = self.get_first_last_timestamp_old()

        # Swap trajectories
        logging.info("Swapping...")
        num_intervals = (last_timestamp - first_timestamp - 1) // self.temporal_thold + 1
        for i in tqdm(range(num_intervals), desc="Num. time intervals"):
            # Get initial and final timestamps of the interval
            ini_t = first_timestamp + i * self.temporal_thold
            end_t = min(ini_t + self.temporal_thold, last_timestamp)

            # Get locations in the interval
            traj_loc_pairs = self.get_locations_in_interval_old(ini_t, end_t)

            # Get possible swaps depending on the distance
            possible_swaps = self.get_possible_swaps_old(traj_loc_pairs)

        # TODO: Get selection of swaps

        # TODO: Perform swaps

        logging.info("Swapping done!")

        # Remove trajectories with less than 1 locations
        logging.info("Remove trajectories with less than 1 locations")
        self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]

        # Remove trajectories without swaps
        logging.info("Remove trajectories without swaps")
        # self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]  # TODO

        logging.info("Done!")

    def get_first_last_timestamp_old(self):
        first_timestamp = float("inf")
        last_timestamp = float("-inf")
        for t in self.anonymized_dataset.trajectories:
            if t.get_first_timestamp() < first_timestamp:
                first_timestamp = t.get_first_timestamp()
            if t.get_last_timestamp() > last_timestamp:
                last_timestamp = t.get_last_timestamp()

        return first_timestamp, last_timestamp

    def get_locations_in_interval_old(self, ini_t: float, end_t: float):
        traj_loc_pairs = []
        for traj in self.anonymized_dataset.trajectories:
            if traj.get_first_timestamp() <= ini_t < traj.get_last_timestamp():  # TODO: Check this
                for loc in traj.locations:
                    if ini_t <= loc.timestamp <= end_t:
                        traj_loc_pairs.append((traj, loc))

        return traj_loc_pairs

    def get_possible_swaps_old(self, traj_loc_pairs):
        possible_swaps = []
        for idx1, (t1, l1) in enumerate(traj_loc_pairs):
            if idx1 < len(traj_loc_pairs) - 1:
                for (t2, l2) in traj_loc_pairs[idx1 + 1:]:
                    if l1.spatial_distance(l2) < self.spatial_thold:
                        possible_swaps.append(((t1, l1), (t2, l2)))

        return possible_swaps

    def swap_old(self, t1: Trajectory, l1: TimestampedLocation, t2: Trajectory, l2: TimestampedLocation):
        return NotImplemented  # TODO

    def get_anonymized_dataset(self):
        return self.anonymized_dataset
