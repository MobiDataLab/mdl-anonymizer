import logging
import random
import numpy as np
from tqdm import tqdm

from src.entities.Dataset import Dataset
from src.entities.Trajectory import Trajectory
from src.entities.TimestampedLocation import TimestampedLocation


class SwapMob:
    def __init__(self, dataset: Dataset, spatial_thold: float, temporal_thold: float, min_n_swaps=1, seed=None):
        self.dataset = dataset
        self.spatial_thold = spatial_thold
        self.temporal_thold = temporal_thold
        self.min_n_swaps = min_n_swaps
        self.seed = seed

        self.anonymized_dataset = dataset.__class__()

    def run(self):
        # Set seed
        if self.seed is not None:
            random.seed(self.seed)

        # Get the original dataset as NumPy array sort by timestamp
        np_dataset = self.dataset.to_numpy(sort_by_timestamp=True)

        # Create dictionary for count amount of swaps per user
        swaps_per_user = self.create_swaps_per_user_dict(np_dataset)

        # Get first and last timestamp of the dataset
        first_timestamp, last_timestamp = self.get_first_and_last_timestamps(np_dataset)

        # Swap trajectories
        logging.info("Swapping...")
        last_end_idx = 0
        interval_idx = 0
        ini_t = end_t = 0
        with tqdm(total=len(np_dataset)) as pbar:
            while end_t < last_timestamp:
                # Get initial and final timestamps of the interval
                ini_t = first_timestamp + interval_idx * self.temporal_thold
                end_t = min(ini_t + self.temporal_thold, last_timestamp)

                # Get initial and end index of the locations in the interval
                locs_in_interval, ini_idx, end_idx = self.get_locs_in_interval(np_dataset, ini_t, end_t, last_end_idx)

                # Update last_end_idx for next interval get
                last_end_idx = end_idx

                # If there are locations in the interval
                if len(locs_in_interval):
                    # Get possible swaps depending on the distance
                    possible_swaps = self.get_possible_swaps(locs_in_interval)

                    # Random matching of possible swaps, returning also the number of swaps performed per user
                    swaps, performed_swaps_per_user = self.compute_random_matchings(possible_swaps, locs_in_interval)

                    # Perform all swaps and update np_dataset
                    np_dataset = self.compute_swaps(np_dataset, swaps, ini_idx)

                    # Update swaps_per_user_dict
                    for (user_id, count) in performed_swaps_per_user.items():
                        swaps_per_user[user_id] += count

                # Increment interval index
                interval_idx += 1

                # Update progress bar
                pbar.update(len(locs_in_interval))

        logging.info("Swapping done!")

        # Remove trajectories without swaps
        logging.info("Remove trajectories without swaps")
        for (user_id, count) in swaps_per_user.items():
            if count < self.min_n_swaps:
                user_id = int(user_id)
                np_dataset = np_dataset[np.argwhere(np_dataset[:, 3] != user_id)[:, 0], :]

        # Transform np_dataset to the anonymized dataset
        logging.info("Transforming NumPy matrix to anonymized dataset")
        self.anonymized_dataset.from_numpy(np_dataset)

        # Remove trajectories with less than 1 locations    # TODO: Remove this? Do it with numpy?
        logging.info("Remove trajectories with less than 1 locations")
        self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]

        logging.info("Done!")

    def create_swaps_per_user_dict(self, np_dataset):
        users_ids = np.unique(np_dataset[:, 3]).astype(int)
        return {str(user_id): 0 for user_id in users_ids}

    def get_first_and_last_timestamps(self, np_dataset):
        """CAUTION: It assumes that np_dataset is sorted by timestamp"""
        first_timestamp = np_dataset[0][2]
        last_timestamp = np_dataset[-1][2]
        return int(first_timestamp), int(last_timestamp)

    def get_locs_in_interval(self, np_dataset, ini_t, end_t, last_end_idx=0):
        """Get locations existing in the time interval [ini_t, end_t]
        last_end_idx is the end_idx of the last call (used for avoiding re-computation)
        CAUTION: It assumes that np_dataset is sorted by timestamp"""
        # Get only the dataset from the last for avoiding re-computation
        considered_dataset = np_dataset[last_end_idx:]

        # If there are locations after the last end index
        if len(considered_dataset) > 0:
            # Get ini and end indeces of locations in interval (np_dataset SORTED BY TIMESTAMP IS ASSUMED)
            # TODO: Maybe np.searchsorted(side="right") would be faster?
            ini_idx = np.argmax(considered_dataset >= ini_t)  # ArgMax gets the first index where condition is true
            end_idx = np.argmax(
                considered_dataset[ini_idx + 1:] > end_t)  # ArgMax gets the first index where condition is true

            # Adjust ini and end indexes to real positions
            ini_idx += last_end_idx
            end_idx += ini_idx + 1  # Used for avoiding future re-computation (next last_end_idx)
        # Otherwise, return and empty array
        else:
            ini_idx = end_idx = 0

        # Get locations in interval
        locs_in_interval = np_dataset[ini_idx:end_idx]

        return locs_in_interval, int(ini_idx), int(end_idx)

    def get_possible_swaps(self, locs_in_interval: np.array) -> list:
        """Obtains all the crossing trajectories in the time interval as possible swaps
        (including the redundant cases of a->b and b->a).
        locs_in_interval is assumed to be ordered by timestamp.
        Returned swaps list is formed by pairs (as tuples) of the loc index and a list of all the close locations indexes,
        sorted by timestamp."""
        # Transform locations in interval to location objects for distance computation
        locations = []
        for loc in locs_in_interval:
            locations.append(TimestampedLocation(loc[2], loc[0], loc[1]))

        # Get possible swaps
        possible_swaps = []
        for idx1, l1 in enumerate(locations):
            # Get close locations
            close_locations = []
            for idx2, l2 in enumerate(locations):
                # If not comparing with the same location or user
                if idx1 != idx2 and locs_in_interval[idx1, 3] != locs_in_interval[idx2, 3]:
                    if l1.spatial_distance(l2) < self.spatial_thold:
                        close_locations.append(idx2)
            # Add to possible_swaps
            if len(close_locations) > 0:
                possible_swaps.append((idx1, close_locations))

        return possible_swaps

    def compute_random_matchings(self, possible_swaps: list, locs_in_interval: np.array):
        """Given a list of possible swaps, selects the swap for each close_locations list
        possible_swaps is assumed to be ordered by timestamp.
        Apart from the swap list, it also returns a dict with the number of swaps performed per user"""

        # Sort possible_swaps by number of close locations (descending) for maximizing the number of total swaps
        possible_swaps.sort(key=lambda x: len(x[1]), reverse=False)

        # Compute swaps
        swaps = []
        swaps_per_user = self.create_swaps_per_user_dict(locs_in_interval)
        i = 0
        while 0 <= i < len(possible_swaps):
            (idx1, close_locations) = possible_swaps[i]

            # Randomly select swapping and add to list
            idx2 = random.choice(close_locations)
            swaps.append((idx1, idx2))

            # Remove from future possible swaps
            j = i + 1
            while 0 < j < len(possible_swaps):
                (idx3, close_locations) = possible_swaps[j]

                # If is the location index, remove possible swap
                if idx3 == idx1 or idx3 == idx2:
                    del possible_swaps[j]
                    # Decrement both i and j indexes because of the removing
                    i -= 1
                    j -= 1
                # Otherwise, try to remove from close locations list
                else:
                    if idx1 in close_locations:
                        close_locations.remove(idx1)
                    if idx2 in close_locations:
                        close_locations.remove(idx2)
                    if len(close_locations) == 0:
                        # Remove possible swap if close_locations is empty
                        del possible_swaps[j]
                        # Decrement both i and j indexes because of the removing
                        i -= 1
                        j -= 1

                # Increment removing index
                j += 1

            # Increment number of swaps per user (used outside for filtering)
            id1 = int(locs_in_interval[idx1, 3])
            swaps_per_user[str(id1)] += 1
            id2 = int(locs_in_interval[idx2, 3])
            swaps_per_user[str(id2)] += 1

            # Increment possible swap index
            i += 1

        return swaps, swaps_per_user

    def compute_swaps(self, np_dataset, swaps: list, ini_idx: int) -> np.array:
        for (raw_idx1, raw_idx2) in swaps:
            # Apply offset to raw indexes computed considering only the locs_in_interval
            idx1 = ini_idx + raw_idx1
            idx2 = ini_idx + raw_idx2

            # Get user ids corresponding the swap
            id1 = np_dataset[idx1][3]
            id2 = np_dataset[idx2][3]

            # If IDs are different
            if id1 != id2:  # TODO: Change previous code for making this impossible
                # Get previous indices of the trajectories
                prev_indices_1 = np.where(np_dataset[:idx1 + 1, 3] == id1)[0]
                prev_indices_2 = np.where(np_dataset[:idx2 + 1, 3] == id2)[0]

                # Perform swap
                np_dataset[prev_indices_1, 3] = id2
                np_dataset[prev_indices_2, 3] = id1

        return np_dataset

    def get_anonymized_dataset(self):
        return self.anonymized_dataset
