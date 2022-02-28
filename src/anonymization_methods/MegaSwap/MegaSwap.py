import logging
import random
import time
from collections import defaultdict
from copy import deepcopy

import haversine
import numpy as np
from tqdm import tqdm

from src.entities.Dataset import Dataset
from src.entities.Trajectory import Trajectory


class MegaSwap:
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
        remaining_locations = []
        for t in self.dataset.trajectories:
            for l in t.locations:
                remaining_locations.append((t.id, l))

        logging.info("Swapping...")
        pbar = tqdm(total=len(remaining_locations))


        while remaining_locations:

            # logging.info(f"Remaining locations: {len(remaining_locations)}")

            # Choose one
            landa = random.choice(remaining_locations)

            # Find all nearest locations
            U = [landa]

            ###################################################################################################
            # VECTORIZING BOTH DISTANCES
            #
            # candidates = np.array([l_1 for l_1 in remaining_locations if l_1[0] != landa[0]])
            # # All the locations within the temporal distance
            # l_timestamp = np.array([landa[1].timestamp])
            # candidates_timestamps = np.array([l_1[1].timestamp for l_1 in candidates])
            #
            # temporal_distances = candidates_timestamps - l_timestamp
            # candidates = candidates[np.where(abs(temporal_distances) <= self.R_t)]
            # if candidates.size > 0:
            #     # From the remaining candidates, those within the haversine distance
            #
            #     l_point = np.array([landa[1].get_coordinates()])
            #     candidates_points = np.array([l1[1].get_coordinates() for l1 in candidates])
            #     spatial_distances = haversine.haversine_vector(l_point, candidates_points, comb=True)
            #     spatial_distances = spatial_distances.flatten()
            #
            #     candidates = candidates[np.where(spatial_distances <= self.R_s)]
            #
            #     if candidates.size > 0:
            #         for c in candidates:
            #             U.append(tuple(c))
            #
            ###################################################################################################
            # VECTORIZING JUST TEMPORAL DISTANCES
            start = time.time()
            candidates = [l_1 for l_1 in remaining_locations if l_1[0] != landa[0]]

            # All the locations within the temporal distance
            l_timestamp = np.array([landa[1].timestamp])
            candidates_timestamps = np.array([l_1[1].timestamp for l_1 in candidates])

            temporal_distances = candidates_timestamps - l_timestamp

            # ca = candidates[np.where(abs(temporal_distances) <= self.R_t)]
            # end = time.time()
            # print(end - start)
            candidates = [c for i, c in enumerate(candidates) if abs(temporal_distances[i]) <= self.R_t]

            if len(candidates) > 0:
                # From the remaining candidates, those within the haversine distance
                for c in candidates:
                    distance = landa[1].spatial_distance(c[1])
                    if 0 <= distance <= self.R_s:
                        U.append(tuple(c))

            end = time.time()
            print(end - start)
            exit()
            ###################################################################################################

            # start = time.time()
            # for l in [l_2 for l_2 in remaining_locations if l_2[0] != landa[0]]:
            #
            #     # Check temporal distance from 'landa' to 'l'
            #     if landa[1].temporal_distance(l[1]) <= self.R_t:
            #         # Check spatial distance from 'landa' to 'l'
            #         distance = landa[1].spatial_distance(l[1])
            #
            #         if 0 <= distance <= self.R_s:
            #             U.append(l)
            # end = time.time()
            # print(end - start)
            # exit()


            if len(U) > 2:
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

