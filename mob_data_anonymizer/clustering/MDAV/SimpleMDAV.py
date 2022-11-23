import logging

from mob_data_anonymizer.clustering.ClusteringInterface import ClusteringInterface
from mob_data_anonymizer.clustering.MDAV.SimpleMDAVDataset import SimpleMDAVDataset
from mob_data_anonymizer.clustering.MDAV.interfaces.MDAVDatasetInterface import MDAVDatasetInterface
from mob_data_anonymizer.entities.Dataset import Dataset

from timeit import default_timer as timer
from tqdm import tqdm
import numpy as np


class SimpleMDAV(ClusteringInterface):
    '''
    This version of MDAV doesn't compute the centroid of unselected register every loop. It always uses the original
    centroid.
    This allows to speed the execution up.
    '''

    def __init__(self, mdav_dataset: MDAVDatasetInterface):
        self.mdav_dataset = mdav_dataset
        self.original_dataset = None

    def set_dataset(self, dataset: Dataset):
        self.mdav_dataset.set_dataset(dataset)

    def set_original_dataset(self, original_dataset: Dataset):
        self.original_dataset = original_dataset

    def run(self, k: int):

        # if 2*k > len(self.mdav_dataset):
        #     raise Exception(f"Only one cluster will be generated: Dataset length={len(self.mdav_dataset)}")

        if k < 2:
            raise Exception("k < 2, does not make sense")

        expected_clusters = len(self.mdav_dataset) / k

        # We compute the centroid just one time
        centroid = self.mdav_dataset.compute_centroid()
        logging.debug(f'Centroid: {centroid}')
        pbar = tqdm(total=expected_clusters)
        while self.mdav_dataset.unselected_length() >= 3 * k:
            # calculate r (farthest from centroid)
            farthest_r, _ = self.mdav_dataset.farthest_from(centroid)
            # calculate s (Farthest from r)
            farthest_s, i = self.mdav_dataset.farthest_from(farthest_r)
            self.mdav_dataset.distances = self.mdav_dataset.distances[:i]+self.mdav_dataset.distances[i+1:]
            # create cluster with r
            self.mdav_dataset.make_cluster(farthest_r, k)
            pbar.update(1)
            # create cluster with s
            self.mdav_dataset.calculate_distances(farthest_s)
            self.mdav_dataset.make_cluster(farthest_s, k)
            pbar.update(1)

        logging.debug(f'Unselected_length: {self.mdav_dataset.unselected_length()}')
        if self.mdav_dataset.unselected_length() >= 2 * k:
            # calculate r (farthest from centroid)
            farthest_r, _ = self.mdav_dataset.farthest_from(centroid)
            self.mdav_dataset.calculate_distances(farthest_r)
            # create cluster with r
            self.mdav_dataset.make_cluster(farthest_r, k)
            pbar.update(1)

        self.mdav_dataset.make_cluster_unselected()
        # logging.info("\tLast cluster made!")
        pbar.update(1)

        pbar.close()

    def get_clusters(self) -> list:
        clusters = {}
        for t_index in self.mdav_dataset.assigned_to:
            # Check if this trajectory has been assigned to a cluster
            c = self.mdav_dataset.assigned_to[t_index]
            t = self.original_dataset.trajectories[t_index]
            try:
                clusters[c].append(t)
            except KeyError:
                clusters[c] = [t]

        return clusters



