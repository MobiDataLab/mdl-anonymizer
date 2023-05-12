import logging
import random
import time
from mob_data_anonymizer.aggregation import TrajectoryAggregationInterface
from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.clustering.ClusteringInterface import ClusteringInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory

DEFAULT_VALUES = {
    "k": 3
}


class Microaggregation(AnonymizationMethodInterface):
    def __init__(self, dataset: Dataset, k=DEFAULT_VALUES['k'],
                 clustering_method: ClusteringInterface = None,
                 aggregation_method: TrajectoryAggregationInterface = None):
        """
                Parameters
                ----------
                dataset : Dataset
                    Dataset to anonymize.
                k : int
                    Minimum number of trajectories to be aggregated in a cluster (default is 3)
                clustering_method : ClusteringInterface, optional
                    Method to cluster the trajectories (Default is SimpleMDAV)
                aggregation_method : TrajectoryAggregationInterface, optional
                    Method to aggregate the trajectories within a cluster (Default is Martinez2021.Aggregation)
                """

        self.dataset = dataset
        self.aggregation_method = aggregation_method
        self.clustering_method = clustering_method

        self.clusters = {}
        self.centroids = {}
        self.anonymized_dataset = dataset.__class__()

        self.k = k

    def run(self):
        logging.info(f"k: {self.k}")
        # Clustering
        logging.info("Starting clustering...")
        for i, t in enumerate(self.dataset.trajectories):
            t.index = i
        self.clustering_method.set_original_dataset(self.dataset)
        start = time.time()
        self.clustering_method.set_dataset(self.dataset)
        self.clustering_method.run(self.k)
        end = time.time()
        logging.info(f"Clustering finished! Time: {end - start}")
        logging.debug(self.clustering_method.mdav_dataset.assigned_to)

        logging.info("Building anonymized dataset...")
        self.clusters = self.clustering_method.get_clusters()

        self.process_clusters()
        self.anonymized_dataset.trajectories.sort(key=lambda t: t.id)

        logging.info('Anonymization finished!')

    def process_clusters(self):
        for c in self.clusters:
            cluster_trajectories = self.clusters[c]

            # Initialize anonymized trajectories
            anon_trajectories = list(map(lambda t: Trajectory(t.id), cluster_trajectories))

            aggregate_trajectory = self.aggregation_method.compute(cluster_trajectories)
            self.centroids[c] = aggregate_trajectory

            # Add to anonymized dataset
            for T in anon_trajectories:
                T.add_locations(aggregate_trajectory.locations)
                self.anonymized_dataset.add_trajectory(T)

    def get_clusters(self):
        return self.clusters

    def get_centroids(self):
        return self.centroids

    def get_anonymized_dataset(self):
        return self.anonymized_dataset
