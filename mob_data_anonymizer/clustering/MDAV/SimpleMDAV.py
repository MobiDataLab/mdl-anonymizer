import logging

from mob_data_anonymizer.clustering.ClusteringInterface import ClusteringInterface
from mob_data_anonymizer.clustering.MDAV.SimpleMDAVDataset import SimpleMDAVDataset
from mob_data_anonymizer.clustering.MDAV.interfaces.MDAVDatasetInterface import MDAVDatasetInterface
from mob_data_anonymizer.entities.Dataset import Dataset

from timeit import default_timer as timer
from tqdm import tqdm


class SimpleMDAV(ClusteringInterface):
    '''
    This version of MDAV doesn't compute the centroid of unselected register every loop. It always uses the original
    centroid.
    This allows to speed the execution up.
    '''

    def __init__(self, mdav_dataset: MDAVDatasetInterface):
        self.mdav_dataset = mdav_dataset

    def set_dataset(self, dataset: Dataset):
        self.mdav_dataset.set_dataset(dataset)

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
            t1 = timer()
            farthest_r = self.mdav_dataset.farthest_from(centroid)
            t2 = timer()
            # print(f"farthest: {t2-t1}")
            self.mdav_dataset.make_cluster(farthest_r, k)
            t3 = timer()
            # print(f"make cluster: {t3-t2}")

            # logging.info(f"\tCluster made! {self.mdav_dataset.cluster_id}")
            pbar.update(1)
            # exit()
            farthest_s = self.mdav_dataset.farthest_from(farthest_r)

            self.mdav_dataset.make_cluster(farthest_s, k)
            # logging.info(f"\tCluster made! {self.mdav_dataset.cluster_id}")
            pbar.update(1)

        logging.debug(f'Unselected_length: {self.mdav_dataset.unselected_length()}')
        if self.mdav_dataset.unselected_length() >= 2 * k:
            farthest_r = self.mdav_dataset.farthest_from(centroid)
            logging.debug(f'Farthest: {farthest_r}')
            self.mdav_dataset.make_cluster(farthest_r, k)
            # logging.info(f"\tCluster made! {self.mdav_dataset.cluster_id}")
            pbar.update(1)

        self.mdav_dataset.make_cluster_unselected()
        # logging.info("\tLast cluster made!")
        pbar.update(1)

        pbar.close()

    def get_clusters(self) -> list:
        clusters = {}
        for t_id in self.mdav_dataset.assigned_to:
            # Check if this trajectory has been assigned to a cluster
            c = self.mdav_dataset.assigned_to[t_id]
            t = self.mdav_dataset.dataset.get_trajectory(t_id)
            try:
                clusters[c].append(t)
            except KeyError:
                clusters[c] = [t]

        return clusters



