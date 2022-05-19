import logging
import random

from haversine import Unit
from tqdm import tqdm

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory
from mob_data_anonymizer.utils import utils

DEFAULT_MAX_R_S = 500
DEFAULT_MIN_R_S = 120
DEFAULT_MAX_R_T = 100
DEFAULT_MIN_R_T = 60
DEFAULT_K = 3

class MegaDynamicSwap:
    def __init__(self, dataset: Dataset, k, max_R_s, max_R_t, min_R_s, min_R_t, step_s=None, step_t=None):
        '''

        :param dataset:
        :param k:
        :param max_R_s: In meters
        :param max_R_t: In seconds
        :param min_R_s: In meters
        :param min_R_t: In seconds
        :param step_s: In meters
        :param step_t: In seconds
        '''
        self.dataset = dataset
        self.anonymized_dataset = dataset.__class__()
        self.k = k
        self.min_R_s = min_R_s
        self.max_R_s = max_R_s
        self.min_R_t = min_R_t
        self.max_R_t = max_R_t
        if not step_s:
            self.step_s = int(abs(max_R_s - min_R_s) / 5)

        if not step_t:
            self.step_t = int(abs(max_R_t - min_R_t) / 5)

    def __build_cluster(self, remaining_locations, chosen_location):

        spatial_distances_computed = {}
        temporal_distances_computed = {}

        for R_t in utils.inclusive_range(self.min_R_t, self.max_R_t, self.step_t if self.step_t > 0 else None):
            for R_s in utils.inclusive_range(self.min_R_s, self.max_R_s, self.step_s if self.step_s > 0 else None):
                U_prima = []

                for i, l in enumerate(remaining_locations):

                    # We don't consider locations of the same trajectory
                    if chosen_location[0] == l[0]:
                        continue

                    # Check temporal distance from 'chosen_location' to 'l'
                    try:
                        temporal_distance = temporal_distances_computed[i]
                    except KeyError:
                        temporal_distance = chosen_location[1].temporal_distance(l[1])
                        temporal_distances_computed[i] = temporal_distance

                    if temporal_distance <= R_t:
                        # Check spatial distance from 'chosen_location' to 'l'
                        try:
                            distance = spatial_distances_computed[i]
                        except KeyError:
                            distance = chosen_location[1].spatial_distance(l[1], unit=Unit.METERS)
                            spatial_distances_computed[i] = distance

                        if 0 <= distance <= R_s:
                            U_prima.append(l)

                # Just one location for trajectory
                # TODO: Keep the temporal closest location to 'chosen_location'
                used_trajectories = set()
                U_prima = [x for x in U_prima if
                           x[0] not in used_trajectories and (used_trajectories.add(x[0]) or True)]

                # Do we have enough locations?
                if len(U_prima) >= self.k - 1:
                    return U_prima

        # No existing cluster
        return None

    def run(self):

        # Create anon trajectories
        for t in self.dataset.trajectories:
            self.anonymized_dataset.add_trajectory(Trajectory(t.id))
        logging.info("Anonymized dataset initialized!")

        # All locations to be swapped in just one list, with her original trajectory
        remaining_locations = []
        for t in self.dataset.trajectories:
            for l in t.locations:
                remaining_locations.append((t.id, l))

        logging.info("Swapping...")
        pbar = tqdm(total=len(remaining_locations))

        while remaining_locations:

            # Choose one
            chosen_location = random.choice(remaining_locations)

            # Find all nearest locations (dynamic radius)
            U = [chosen_location]

            U_prima = self.__build_cluster(remaining_locations, chosen_location)
            if U_prima:
                U.extend(U_prima)

            if len(U) >= self.k:
                # Assign every location to a random trajectory
                trajectories_id = [l[0] for l in U]
                random.shuffle(U)

                for i, l in enumerate(U):
                    an_t = self.anonymized_dataset.get_trajectory(trajectories_id[i])
                    an_t.add_location(l[1])

            # Remove from remaining_locations
            for l in U:
                remaining_locations.remove(l)

            pbar.update(len(U))

        logging.info("Swapping done!")

        self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]
        logging.info("Removed trajectories with less than 1 locations!\n")

        logging.info("Done!")

    def get_anonymized_dataset(self):
        return self.anonymized_dataset

    @staticmethod
    def get_instance(data):

        # Check if all specific fields exists
        max_r_s = data.get("Max_r_s")
        if not max_r_s:
            logging.info(f"No 'max_r_s' provided. Using {DEFAULT_MAX_R_S} m.")
            max_r_s = DEFAULT_MAX_R_S

        min_r_s = data.get("Min_r_s")
        if not min_r_s:
            logging.info(f"No 'min_r_s' provided. Using {DEFAULT_MIN_R_S} m.")
            min_r_s = DEFAULT_MIN_R_S

        max_r_t = data.get("Max_r_t")
        if not max_r_t:
            logging.info(f"No 'max_r_t' provided. Using {DEFAULT_MAX_R_T} s.")
            max_r_t = DEFAULT_MAX_R_T

        min_r_t = data.get("Min_r_t")
        if not min_r_t:
            logging.info(f"No 'min_r_t' provided. Using {DEFAULT_MIN_R_T} s.")
            min_r_t = DEFAULT_MIN_R_T

        k = data.get("k")
        if not k:
            logging.info(f"No 'k' provided. Using {DEFAULT_K}.")
            k = DEFAULT_K

        dataset = Dataset()
        dataset.load_from_scikit(data.get("input"), min_locations=5, datetime_key="timestamp")
        dataset.filter_by_speed()

        return MegaDynamicSwap(dataset, k, max_r_s, max_r_t, min_r_s, min_r_t)