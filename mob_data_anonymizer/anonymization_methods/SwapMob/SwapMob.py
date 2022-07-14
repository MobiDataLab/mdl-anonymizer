import logging
import random
import numpy as np
from tqdm import tqdm

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory
from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation

DEFAULT_VALUES = {
    "spatial_thold": 0.2,
    "temporal_thold": 30,
}

class SwapMob:
    """Implements the SwapMob anonymization method from Julián Salas, David Megías & Vicenç Torra ( https://doi.org/10.1007/978-3-319-99771-1_22 )"""

    def __init__(self, dataset: Dataset, spatial_thold: float, temporal_thold: float,
                 min_n_swaps: int = 1, seed: int = None):
        """
        Parameters
        ----------
        dataset : Dataset
            Dataset to anonymize.
        spatial_thold : float
            Maximum distance (in kilometers) to consider two locations as close.
        temporal_thold : float
            Maximum time difference (in seconds) to consider two locations as coexistent.
        min_n_swaps : int, optional
            Minimum number of swaps for a trajectory for not being removed. (default is 1)
        seed : int, optional
            Seed for the random swapping process (default is None, so seed is not fixed)
        """
        self.dataset = dataset
        self.spatial_thold = spatial_thold
        self.temporal_thold = temporal_thold
        self.min_n_swaps = min_n_swaps
        self.seed = seed

        self.anonymized_dataset = dataset.__class__()

    def run(self):
        """Performs the SwapMob anonymization method.

        During the execution will transform the original dataset to NumPy for faster processing.
        It will create a new dataset and assign it to the self.anonymized_dataset variable.
        This new dataset can be obtained with the get_anonymized_dataset method.
        A tqdm progress bar is used.
        """
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
                locs_in_interval, ini_idx, end_idx = self.get_locs_in_interval(np_dataset, end_t, last_end_idx)

                # Update last_end_idx for next interval get
                last_end_idx = end_idx

                # If there are locations in the interval
                if len(locs_in_interval) > 0:
                    # Get possible swaps depending on the distance
                    possible_swaps = self.get_possible_swaps(locs_in_interval)

                    # Random matching of possible swaps
                    swaps = self.select_random_swaps(possible_swaps, locs_in_interval)

                    # Perform all swaps on np_dataset, returning also a dictionary with the number of swaps performed per user
                    performed_swaps_per_user = self.do_swaps(np_dataset, swaps, ini_idx)

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

        logging.info("Done!")

    def create_swaps_per_user_dict(self, np_dataset: np.array) -> dict:
        """Creates a dictionary for counting the number of swaps per user id.
        Used for min_n_swaps filtering.

        Parameters
        ----------
        np_dataset : np.array
            NumPy array version of the original dataset.

        Returns
        -------
        swaps_per_user : dict
            A dictionary with integer user_ids passed to string as keys and
            values intialized to zero.
        """
        users_ids = np.unique(np_dataset[:, 3]).astype(int)
        return {str(user_id): 0 for user_id in users_ids}

    def get_first_and_last_timestamps(self, np_dataset: np.array) -> tuple:
        """Obtains the first and last timestamps of the dataset.

        CAUTION: It assumes that np_dataset is sorted by timestamp.

        Parameters
        ----------
        np_dataset : np.array
            NumPy array version of the original dataset sorted by timestamp.

        Returns
        -------
        first_and_last : tuple
            A tuple with first and last timestamps.
        """
        first_timestamp = np_dataset[0][2]
        last_timestamp = np_dataset[-1][2]
        return int(first_timestamp), int(last_timestamp)

    def get_locs_in_interval(self, np_dataset: np.array, end_t: int, last_end_idx: int = 0) -> tuple:
        """Gets locations existing from the last_end_idx to that with a timestamp greater or equal to end_t (equivalent to [ini_t, end_t]).

        CAUTION 1: It assumes that np_dataset is sorted by timestamp.
        CAUTION 2: It is possible that none locations are found in the interval.
        last_end_idx is the end_idx of the last call (used for avoiding re-computation) and it will be the returned ini_idx.

        Parameters
        ----------
        np_dataset : np.array
            NumPy array version of the dataset sorted by timestamp.
        end_t : int
            Last timestamp to consider in the interval (included).
        last_end_idx : int, optional
            Last end index returned for the method (default is 0).
            Used for avoiding re-computation. It will be returned as ini_idx.

        Returns
        -------
        locs_in_interval, ini_idx, end_idx : tuple
            A tuple with the section np_dataset of that interval (maybe empty) and the initial (equal to last_end_idx) and end indexes (maybe equal).
        """

        # If there are locations after the last end index (not guaranteed due to float precision errors in computing end_t)
        if last_end_idx < len(np_dataset):
            # Initial index is assumed to be last_end_idx (end_idx of the previous interval)
            ini_idx = last_end_idx

            # Search the end index based on end_t after ini_idx, since np_dataset is sorted by timestamp
            end_idx = np.searchsorted(np_dataset[ini_idx:, 2], end_t, side="right")

            # Add offset
            end_idx += last_end_idx
        # Otherwise, return and empty array
        else:
            ini_idx = end_idx = 0

        # Get locations in interval
        locs_in_interval = np_dataset[ini_idx:end_idx]

        return locs_in_interval, int(ini_idx), int(end_idx)

    def get_possible_swaps(self, locs_in_interval: np.array) -> list:
        """Obtains all the crossing trajectories in the time interval.

        CAUTION: locs_in_interval is assumed to be ordered by timestamp.
        It avoids swaps between locations of the same user, but redundant cases (such as a->b and b->a) are kept
        for its usage at the select_random_swaps method.
        This redundancy is required for maxmimizing the number of swaps.

        Parameters
        ----------
        locs_in_interval : np.array
            Section of the np_dataset with locations in the current interval.
            Returned by the get_locs_in_interval method.

        Returns
        -------
        possible_swaps : list
            List of possible swaps. Each value is a tuple with the location index (within locs_in_inverval array) and
            a list of the close locations indexes (also within locs_in_interval array).
        """
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
                    # If locations are closer than the threshold
                    if l1.spatial_distance(l2) < self.spatial_thold:
                        close_locations.append(idx2)
            # Add to possible_swaps
            if len(close_locations) > 0:
                possible_swaps.append((idx1, close_locations))

        return possible_swaps

    def select_random_swaps(self, possible_swaps: list, locs_in_interval: np.array) -> list:
        """Randomly selects the swaps to perform from the possible_swaps list.

        Equivalent to the random matching method from the SwapMob article.
        Avoids problematic swaps such as those with already swapped users or between locations from the same user.
        Due to that it is not guaranteed that every location in possible_swaps obtains a swap.

        Parameters
        ----------
        possible_swaps : list
            List of possible swaps returned by the get_possible_swaps method.
        locs_in_interval : np.array
            NumPy array section of the np_dataset returned by the get_locs_in_interval method.

        Returns
        -------
        swaps : list
            List containing the swaps. Each element is tuple with the indexes pair of locations to swap (within locs_in_interval).
            Pairs are sorted by timestamp.
        """
        # Sort possible_swaps by number of close locations (descending) for maximizing the number of total swaps
        possible_swaps.sort(key=lambda x: len(x[1]), reverse=False)

        # Compute swaps
        swaps = []
        i = 0
        while i < len(possible_swaps):
            (idx1, close_locations) = possible_swaps[i]

            # Randomly select swapping
            idx2 = random.choice(close_locations)

            # Sort indexes by timestamp
            if locs_in_interval[idx1, 2] > locs_in_interval[idx2, 2]:
                # Swap variables (idx1 <-> idx2)
                idx1 = idx1 + idx2
                idx2 = idx1 - idx2
                idx1 = idx1 - idx2

            # Add to swaps list
            swaps.append((idx1, idx2))

            # Remove user ids from swaps of future possible swaps
            id1 = locs_in_interval[idx1, 3]
            id2 = locs_in_interval[idx2, 3]
            j = i + 1
            while j < len(possible_swaps):
                (idx3, close_locations) = possible_swaps[j]

                # If repeated location index or user_id, remove possible swap
                id3 = locs_in_interval[idx3, 3]
                if idx3 == idx1 or id3 == id1 or idx3 == idx2 or id3 == id2:
                    del possible_swaps[j]
                    j -= 1  # Decrement index because of the removing
                # Otherwise, try to remove from close locations list
                else:
                    k = 0
                    while k < len(close_locations):
                        idx4 = close_locations[k]
                        id4 = locs_in_interval[idx4, 3]
                        # If repeated location index or user_id, remove close location
                        if idx4 == idx1 or id4 == id1 or idx4 == idx2 or id4 == id2:
                            del close_locations[k]
                            k -= 1  # Decrement index because of the removing
                        k += 1  # Increment index
                    # Remove possible swap if close_locations is empty
                    if len(close_locations) == 0:
                        del possible_swaps[j]
                        j -= 1  # Decrement index because of the removing
                j += 1  # Increment index

            # Increment possible swap index
            i += 1

        return swaps

    def do_swaps(self, np_dataset: np.array, swaps: list, ini_idx: int) -> dict:
        """Performs the swaps as defined in the SwapMob article.

        For each pair of indexes of locations from the swaps list, swaps the user ids of all the previous locations.
        Directly modifies the np_dataset during the swaps.

        Parameters
        ----------
        np_dataset : np.array
            NumPy array version of the dataset. Will be modified during the method.
        swaps : list
            List of swaps returned by the select_random_swaps method.
        ini_idx : int
            Initial index of the locations of the current interval.
            Used as offset for the swaps from the swaps list.

        Returns
        -------
        swaps_per_user : dict
            Dictionary containing the number of swaps for each user_id (as integer transformed to string).
            Used for updating the global swaps_per_user dictionary in the run method.
        """
        # Dictionary for storing number of swaps per user (used outside for filtering)
        swaps_per_user = {}

        # Perform all swaps
        for (raw_idx1, raw_idx2) in swaps:
            # Apply offset to raw indexes computed considering only locs_in_interval
            idx1 = ini_idx + raw_idx1
            idx2 = ini_idx + raw_idx2

            # Get user ids corresponding the swap
            id1 = np_dataset[idx1, 3]
            id2 = np_dataset[idx2, 3]

            # Get previous indices of the trajectories
            prev_indices_1 = np.where(np_dataset[:idx1 + 1, 3] == id1)[0]
            prev_indices_2 = np.where(np_dataset[:idx2 + 1, 3] == id2)[0]

            # Perform swap
            np_dataset[prev_indices_1, 3] = id2
            np_dataset[prev_indices_2, 3] = id1

            # Increment number of swaps per user (used outside for filtering)
            id1_str = str(int(id1))
            swaps_per_user[id1_str] = swaps_per_user.get(id1_str, 0) + 1
            id2_str = str(int(id2))
            swaps_per_user[id2_str] = swaps_per_user.get(id2_str, 0) + 1

        return swaps_per_user

    def get_anonymized_dataset(self) -> Dataset:
        """Returns
        -------
        anonymized_dataset : Dataset
            The anonymized dataset computed at the run method"""
        return self.anonymized_dataset


    @staticmethod
    def get_instance(data):

        required_fields = ["spatial_thold", "temporal_thold"]
        values = {}

        for field in required_fields:
            values[field] = data.get(field)
            if not values[field]:
                logging.info(f"No '{field}' provided. Using {DEFAULT_VALUES[field]}.")
                values[field] = DEFAULT_VALUES[field]

        dataset = Dataset()
        dataset.load_from_scikit(data.get("input_file"), min_locations=5, datetime_key="timestamp")
        dataset.filter_by_speed()

        min_n_swaps = data.get('min_n_swaps', 1)
        seed = data.get('seed', None)

        return SwapMob(dataset,
                       values['spatial_thold'], values['temporal_thold'],
                       min_n_swaps=min_n_swaps, seed=seed)