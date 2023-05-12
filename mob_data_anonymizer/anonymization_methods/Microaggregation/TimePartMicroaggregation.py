import logging
import time
from mob_data_anonymizer.aggregation import TrajectoryAggregationInterface
from mob_data_anonymizer.clustering.ClusteringInterface import ClusteringInterface
from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory
from tqdm import tqdm

DEFAULT_VALUES = {
    "k": 3,
    "interval": 900
}


class TimePartMicroaggregation(AnonymizationMethodInterface):
    def __init__(self, dataset: Dataset, k=DEFAULT_VALUES['k'],
                 clustering_method: ClusteringInterface = None,
                 aggregation_method: TrajectoryAggregationInterface = None,
                 interval: int = 15*60):
        """
                Parameters
                ----------
                dataset : Dataset
                    Dataset to anonymize.
                k : int
                    Mínimium number of trajectories to be aggregated in a cluster (default is 3)
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
        self.interval = interval

    def run(self):
        logging.info(f"k: {self.k}")
        logging.info(f"Interval: {self.interval}")
        # Partition
        for i, t in enumerate(self.dataset.trajectories):
            t.index = i
        datasets = []
        ordered_trajectories = sorted(self.dataset.trajectories, key=lambda t: t.locations[0].timestamp)
        while len(ordered_trajectories) >= self.k:
            partition = []
            current_t = ordered_trajectories[0].locations[0].timestamp
            final_t = current_t + self.interval
            index = 0
            while current_t <= final_t and index < len(ordered_trajectories)-1:
                partition.append(ordered_trajectories[index])
                index += 1
                current_t = ordered_trajectories[index].locations[0].timestamp
            if len(partition) < self.k:
                while len(partition) < self.k:
                    partition.append(ordered_trajectories[index])
                    index += 1
            dataset = Dataset()
            dataset.trajectories = partition
            datasets.append(dataset)
            ordered_trajectories = ordered_trajectories[index:]
        datasets[-1].trajectories.extend(ordered_trajectories)

        # Clustering
        self.clustering_method.set_original_dataset(self.dataset)
        start = time.time()
        logging.info("Starting clustering...")
        # for i, dataset in enumerate(datasets):
        for i, dataset in enumerate(tqdm(datasets)):
            # logging.info(f"Starting clustering...{i+1} of {len(datasets)}")
            self.clustering_method.set_dataset(dataset)
            self.clustering_method.run(self.k)
            # logging.info("Building anonymized dataset...")
            self.clusters = self.clustering_method.get_clusters()
            self.process_clusters()
        logging.info("Building anonymized dataset...")
        self.anonymized_dataset.trajectories.sort(key=lambda t: t.id)
        end = time.time()
        logging.info(f"Clustering finished! Time: {end - start}")
        logging.debug(self.clustering_method.mdav_dataset.assigned_to)
        logging.info('Anonymization finished!')

    def process_clusters(self):
        for c in self.clusters:
            cluster_trajectories = self.clusters[c]

            # Initialize anonymized trajectories
            anon_trajectories = list(map(lambda t: Trajectory(t.id, t.user_id), cluster_trajectories))

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
