import logging
import random
import time
from collections import defaultdict
from copy import deepcopy

import haversine
import numpy as np
from tqdm import tqdm

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mob_data_anonymizer.entities.Trajectory import Trajectory


class MegaSwapOptimized:
    def __init__(self, dataset: Dataset, R_s, R_t):
        self.dataset = dataset
        self.anonymized_dataset = dataset.__class__()
        self.R_s = R_s
        self.R_t = R_t

    def run(self):

        # Create anon trajectories
        for t in self.dataset.trajectories:
            self.anonymized_dataset.add_trajectory(Trajectory(t.id))
        logging.info("Anonymized dataset initialized!")

        # All locations to be swapped in just one list, with her original trajectory
        # remaining_locations = []
        # for t in self.dataset.trajectories:
        #     for l in t.locations:
        #         remaining_locations.append((t.id, l))

        remaining_locations = []
        for t in self.dataset.trajectories:
            for l in t.locations:
                remaining_locations.append(np.array([t.id, l.x, l.y, l.timestamp]))

        np_remaining_locations = np.array(remaining_locations).astype(np.float32)

        logging.info("Swapping...")
        pbar = tqdm(total=len(remaining_locations))

        while len(np_remaining_locations) > 0:

            # logging.info(f"Remaining locations: {len(remaining_locations)}")

            # Choose one
            landa = np_remaining_locations[np.random.choice(np_remaining_locations.shape[0])]

            # Find all nearest locations
            U = np.array([landa])

            candidates = np_remaining_locations[np.where(np_remaining_locations[:, 0] != landa[0])]

            l_timestamp = landa[3]
            candidates_timestamps = candidates[:, 3]

            temporal_distances = np.abs(candidates_timestamps - l_timestamp)

            indexes = np.argwhere(temporal_distances <= self.R_t).flatten()

            selected_candidates = candidates[indexes]

            spatial_distances = haversine.haversine_vector(landa[1:3], selected_candidates[:, 1:3], comb=True).flatten()

            selected_candidates = selected_candidates[np.argwhere(spatial_distances <= self.R_s).flatten()]

            U = np.vstack((U, selected_candidates))

            if len(U) > 2:
                # Assign every location to a random trajectory
                np.random.shuffle(U[:,0])

                for c in U:
                    an_t = self.anonymized_dataset.get_trajectory(c[0])
                    an_t.add_location(TimestampedLocation(c[3], c[1], c[2]))

            # Remove from np_remaining_locations
            np_remaining_locations = np_remaining_locations[~np.all(np.isin(np_remaining_locations, U), axis=1)]

            pbar.update(len(U))

        logging.info("Swapping done!")

        self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]
        logging.info("Removed trajectories with less than 1 locations!\n")

        logging.info("Done!")

    def get_anonymized_dataset(self):
        return self.anonymized_dataset
