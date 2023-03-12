import logging
import random

import pandas
from haversine import Unit, haversine, haversine_vector
from tqdm import tqdm
import numpy as np

from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.anonymization_methods.SwapLocations.trajectory_anonymization import \
    apply_trajectory_anonymization
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory
from mob_data_anonymizer.utils import utils

DEFAULT_VALUES = {
    "k": 3,
    "max_r_s": 500,
    "min_r_s": 100,
    "max_r_t": 120,
    "min_r_t": 60,
    "tile_size": 1000,
}


class SwapLocations(AnonymizationMethodInterface):
    def __init__(self, dataset: Dataset, k=DEFAULT_VALUES['k'],
                 max_r_s=DEFAULT_VALUES['max_r_s'], max_r_t=DEFAULT_VALUES['max_r_t'],
                 min_r_s=DEFAULT_VALUES['min_r_s'], min_r_t=DEFAULT_VALUES['min_r_t'],
                 step_s=None, step_t=None, tile_size=DEFAULT_VALUES['tile_size'],
                 seed: int = None):
        """
        Parameters
        ----------
        dataset : Dataset
            Dataset to anonymize.
        k : int, optional
            Minimum number of locations of a swapping cluster (default is 3)
        max_r_s: int, optional
            Maximum spatial radius of the swapping cluster (in meters, default is 500)
        max_r_t: int, optional
            Maximum temporal threshold of the swapping cluster (in seconds, default is 100)
        min_r_s: int, optional
            Minimum spatial radius of the swapping cluster (in meters, default is 120)
        min_r_t: int, optional
            Minimum temporal threshold of the swapping cluster (in seconds, default is 60)
        step_s: int, optional
            In meters
        step_t: int, optional
            In seconds
        tile_size: int, optional
            Size of the tiles in tessellation used for trajectory anonymization (in meters)
        seed : int, optional
            Seed for the random swapping process (default is None, so seed is not fixed)
        """

        self.dataset = dataset
        self.anonymized_dataset = dataset.__class__()
        self.k = k
        self.min_r_s = min_r_s
        self.max_r_s = max_r_s
        self.min_r_t = min_r_t
        self.max_r_t = max_r_t
        if not step_s:
            self.step_s = int(abs(max_r_s - min_r_s) / 2)

        if not step_t:
            self.step_t = int(abs(max_r_t - min_r_t) / 2)

        self.tile_size = tile_size
        self.seed = seed

    def __build_cluster(self, tdf, l):

        temporal_range = utils.inclusive_range(self.min_r_t, self.max_r_t, self.step_t if self.step_t > 0 else None)
        spatial_range = utils.inclusive_range(self.min_r_s, self.max_r_s, self.step_s if self.step_s > 0 else None)

        timestamp = l.iloc[0]['datetime']

        # Compute the time difference between this timestamped_location and the rest of locations in the tdf
        tdf['dif_time'] = np.abs((tdf['datetime'] - timestamp).dt.total_seconds())

        for R_t in temporal_range:

            # Compute the locations in the temporal range (tfd2 just keeps the locations within the temporal range)
            tdf2 = tdf.query('dif_time <= @R_t').copy()

            # If not enough locations, check the next range
            if len(tdf2) < self.k:
                continue

            # We have enough locations, check the spatial range

            # Compute all the distances from tdf2 points to our timestamped_location
            tdf2['distance'] = haversine_vector(tdf2[['lat', 'lng']].to_numpy(), l[['lat', 'lng']].to_numpy(),
                                                unit=Unit.METERS, comb=True).flatten()

            for R_s in spatial_range:
                # tdf3 has all the locations inside both temporal and spatial range
                tdf3 = tdf2.query('distance <= @R_s').copy()
                # Keep just one location for each trajectory (don't swap locations of the same trajectory)
                # We keep the locations temporally closer to the original one
                tdf3 = tdf3.sort_values(by=['dif_time'])
                tdf3 = tdf3.drop_duplicates(subset=['tid'], keep='first')

                # If not enough locations, check the next spatial range
                if len(tdf3) < self.k:
                    continue

                # We have enough locations!
                return tdf3

        # There is no possible cluster
        return None

    def run(self):
        num_cluster = 1
        pandas.options.display.width = 0
        anon_tdf = pandas.DataFrame()

        tdf = self.dataset.to_tdf()

        pbar = tqdm(total=len(tdf))

        while not tdf.empty:

            l = tdf.sample(random_state=self.seed)

            cluster = self.__build_cluster(tdf, l)

            if cluster is not None:
                # We have a cluster!
                # Remove locations to be swapped from original tdf
                tdf = tdf.drop(cluster.index.tolist())

                # Assign random trajectory to each location
                cluster[['tid', 'uid']] = np.random.permutation(cluster[['tid', 'uid']])

                cluster['num_cluster'] = num_cluster

                anon_tdf = pandas.concat([anon_tdf, cluster], ignore_index=True)
                num_cluster += 1
                pbar.update(len(cluster))
            else:
                # Remove original location from tdf
                tdf = tdf.drop(l.index.tolist())
                pbar.update(len(l))

        # Remove trajectories with just one location
        s = anon_tdf['tid'].value_counts()
        anon_tdf = anon_tdf[anon_tdf['tid'].map(s) >= 2]

        anon_tdf = anon_tdf.sort_values(by=['tid', 'datetime'])

        # anon_tdf.to_csv("anonymized_dataset_details_pre_traj.csv")

        logging.info("Apply trajectory anonymization")
        anon_tdf = apply_trajectory_anonymization(anon_tdf, tile_size=self.tile_size)
        # anon_tdf.to_csv("anonymized_dataset_details_pre_remove_1loc.csv")

        # Remove again trajectories with just one location
        s = anon_tdf['tid'].value_counts()
        anon_tdf = anon_tdf[anon_tdf['tid'].map(s) >= 2]

        self.anonymized_dataset.from_tdf(anon_tdf)

    def get_anonymized_dataset(self):
        return self.anonymized_dataset

    @staticmethod
    def get_instance(data, file=None):

        required_fields = ["k", "max_r_s", "min_r_s", "max_r_t", "min_r_t"]
        values = {}

        for field in required_fields:
            values[field] = data.get(field)
            if not values[field]:
                logging.info(f"No '{field}' provided. Using {DEFAULT_VALUES[field]}.")
                values[field] = DEFAULT_VALUES[field]

        dataset = Dataset()
        if file is None:
            filename = data.get("input_file")
        else:
            filename = file
        dataset.from_file(filename, min_locations=5, datetime_key="timestamp")
        dataset.filter_by_speed()

        step_s = data.get('step_s', None)
        step_t = data.get('step_t', None)
        tile_size = data.get('tile_size', None)

        return SwapLocations(dataset,
                             values['k'], values['max_r_s'], values['max_r_t'], values['min_r_s'], values['min_r_t'],
                             step_s=step_s, step_t=step_t, tile_size=tile_size)
