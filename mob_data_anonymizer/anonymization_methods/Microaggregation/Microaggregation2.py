import logging
import time
from mob_data_anonymizer.aggregation import TrajectoryAggregationInterface
from mob_data_anonymizer.aggregation.Martinez2021.Aggregation import Aggregation
from mob_data_anonymizer.clustering.ClusteringInterface import ClusteringInterface
from mob_data_anonymizer.clustering.MDAV.SimpleMDAV import SimpleMDAV
from mob_data_anonymizer.clustering.MDAV.SimpleMDAVDataset import SimpleMDAVDataset
from mob_data_anonymizer.distances.trajectory.DistanceInterface import DistanceInterface
from mob_data_anonymizer.distances.trajectory.Martinez2021.Distance import Distance
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory

DEFAULT_VALUES = {
    "k": 3
}

class Microaggregation:
    def __init__(self, dataset: Dataset, k=DEFAULT_VALUES['k'], clustering_method: ClusteringInterface = None,
                 distance: DistanceInterface = None, aggregation_method: TrajectoryAggregationInterface = None):
        """
                Parameters
                ----------
                dataset : Dataset
                    Dataset to anonymize.
                k : int
                    Mínimium number of trajectories to be aggregated in a cluster (default is 3)
                clustering_method : ClusteringInterface, optional
                    Method to cluster the trajectories (Default is SimpleMDAV)
                distance : DistanceInterface, optional
                    Method to compute the distance between two trajectories (Default is Martinez2021.Distance)
                aggregation_method : TrajectoryAggregationInterface, optional
                    Method to aggregate the trajectories within a cluster (Default is Martinez2021.Aggregation)
                """

        self.dataset = dataset
        self.distance = distance if distance else Distance(dataset)
        self.aggregation_method = aggregation_method if aggregation_method else Aggregation
        self.clustering_method = clustering_method if clustering_method \
            else SimpleMDAV(SimpleMDAVDataset(dataset, self.distance, self.aggregation_method))

        self.clusters = {}
        self.centroids = {}
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

    @staticmethod
    def get_instance(data):

        required_fields = ["k"]
        values = {}

        for field in required_fields:
            values[field] = data.get(field)
            if not values[field]:
                logging.info(f"No '{field}' provided. Using {DEFAULT_VALUES[field]}.")
                values[field] = DEFAULT_VALUES[field]

        dataset = Dataset()
        dataset.from_file(data.get("input_file"), min_locations=5, datetime_key="timestamp")
        dataset.filter_by_speed()

        #Trajectory Distance
        l = data.get('lambda')

        martinez21_distance = Distance(dataset, landa=l)

        return Microaggregation(dataset, k=values['k'], distance=martinez21_distance)
