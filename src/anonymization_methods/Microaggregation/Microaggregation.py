import logging
import random
import time
from src.aggregation import TrajectoryAggregationInterface
from src.aggregation.Martinez2021.Aggregation import Aggregation
from src.clustering.ClusteringInterface import ClusteringInterface
from src.clustering.MDAV.SimpleMDAV import SimpleMDAV
from src.clustering.MDAV.SimpleMDAVDataset import SimpleMDAVDataset
from src.distances.trajectory.DistanceInterface import DistanceInterface
from src.distances.trajectory.Martinez2021.Distance import Distance
from src.entities import Dataset
from src.entities.Trajectory import Trajectory


class Microaggregation:
    def __init__(self, dataset: Dataset, k=3, clustering_method: ClusteringInterface = None,
                 distance: DistanceInterface = None, aggregation_method: TrajectoryAggregationInterface = None):

        self.dataset = dataset
        self.distance = distance if distance else Distance(dataset)
        self.aggregation_method = aggregation_method if aggregation_method else Aggregation
        self.clustering_method = clustering_method if clustering_method \
            else SimpleMDAV(SimpleMDAVDataset(dataset, self.distance, self.aggregation_method))

        self.clusters = {}
        self.anonymized_dataset = dataset.__class__()

        self.k = k

    def run(self):

        # Clustering
        logging.info("Starting clustering...")
        start = time.time()
        self.clustering_method.set_dataset(self.dataset)
        self.clustering_method.run(self.k)
        end = time.time()
        logging.info(f"Clustering finished! Time: {end - start}")
        logging.debug(self.clustering_method.mdav_dataset.assigned_to)

        logging.info("Building anonymized dataset...")
        self.clusters = self.clustering_method.get_clusters()

        self.process_clusters()

        logging.info('Anonymization finished!')

    def get_anonymized_dataset(self):
        return self.anonymized_dataset

    def process_clusters(self):
        for c in self.clusters:
            cluster_trajectories = self.clusters[c]

            # Initialize anonymized trajectories
            anon_trajectories = list(map(lambda t: Trajectory(t.id), cluster_trajectories))

            aggregate_trajectory = self.aggregation_method.compute(cluster_trajectories)

            # Add to anonymized dataset
            for T in anon_trajectories:
                T.add_locations(aggregate_trajectory.locations)

                self.anonymized_dataset.add_trajectory(T)