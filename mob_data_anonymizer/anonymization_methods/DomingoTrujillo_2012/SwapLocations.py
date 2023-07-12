import logging
import random
import time

from haversine import Unit

from mob_data_anonymizer.aggregation.Martinez2021.mean_trajectory import Mean_trajectory
from mob_data_anonymizer.aggregation.TrajectoryAggregationInterface import TrajectoryAggregationInterface
from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.clustering.ClusteringInterface import ClusteringInterface
from mob_data_anonymizer.clustering.MDAV.SimpleMDAV import SimpleMDAV
from mob_data_anonymizer.clustering.MDAV.SimpleMDAVDataset import SimpleMDAVDataset
from mob_data_anonymizer.distances.trajectory.DistanceInterface import DistanceInterface
from mob_data_anonymizer.distances.trajectory.DomingoTrujillo2012.Distance import Distance
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mob_data_anonymizer.entities.Trajectory import Trajectory


DEFAULT_VALUES = {
    "k": 3,
    "R_t": 30,
    "R_s": 1000,
}

class SwapLocations(AnonymizationMethodInterface):
    def __init__(self, dataset: Dataset, k=DEFAULT_VALUES['k'], R_t=DEFAULT_VALUES['R_t'], R_s=DEFAULT_VALUES['R_s'],
                 clustering_method: ClusteringInterface = None,
                 aggregation_method: TrajectoryAggregationInterface = None):
        """

        :param dataset : Dataset
            Dataset to anonymize.
        :param k : int
            Minimum number of trajectories to be aggregated in a cluster (default is 3)
        :param R_t: in minutes
        :param R_s: in meters
        :param clustering_method : ClusteringInterface, optional
            Method to cluster the trajectories (Default is SimpleMDAV)
        :param aggregation_method : TrajectoryAggregationInterface, optional
            Method to aggregate the trajectories within a cluster (Default is Martinez2021.Aggregation)
        """
        self.dataset = dataset
        self.aggregation_method = aggregation_method
        self.clustering_method = clustering_method

        self.clusters = {}
        self.anonymized_dataset = dataset.__class__()

        self.k = k
        self.R_t = R_t
        self.R_s = R_s

    def run(self):

        # Filter dataset. We take just the main component of the distance graph
        # filtered_dataset = self.distance.filter_dataset()
        # logging.info(f"Dataset filtered by main component. Now it has {len(filtered_dataset)} trajectories.")

        # Clustering
        logging.info("Starting clustering!")
        logging.info(f"k: {self.k}")

        self.clustering_method.run(self.k)

        logging.info(f"Clustering finished! ")
        logging.debug(self.clustering_method.mdav_dataset.assigned_to)

        logging.info("Swapping locations!")
        self.clusters = self.clustering_method.get_clusters()

        self.process_clusters()

        logging.info('Anonymization finished!')

    def process_clusters(self):
        triples_swapped = []
        for c in self.clusters:

            cluster_trajectories = self.clusters[c]

            # Initialize anonymized trajectories
            anon_trajectories = list(map(lambda t: Trajectory(t.id), cluster_trajectories))

            # Let T be a random trajectory in C
            T = random.choice(cluster_trajectories)

            # For all "unswapped" locations in T
            unswapped_locations = [l for l in T.locations if (T.id, l.timestamp, l.x, l.y) not in triples_swapped]
            for landa in unswapped_locations:

                # Initialize U = {landa}
                U = [(T.id, landa)]

                # For all trajectories t_p in C with t_p != T
                for T_p in [traj for traj in cluster_trajectories if traj != T]:
                    # Look for an "unswapped" triple 'l' minimizing the intra-cluster distance in U and such that:
                    d = 99999999
                    landa_p = None

                    # Check locations not swapped yet
                    for l in [l for l in T_p.locations if (T_p.id, l.timestamp, l.x, l.y) not in triples_swapped]:

                        # Check temporal distance from 'landa' to 'l'
                        if landa.temporal_distance(l) <= self.R_t:
                            # Check spatial distance from 'landa' to 'l'
                            if 0 <= landa.spatial_distance(l, unit=Unit.METERS) <= self.R_s:
                                # We take the location with the minimum intra-cluster distance
                                if TimestampedLocation.compute_centroid([tuple[1] for tuple in U]).distance(l) < d:
                                    d = landa.distance(l)
                                    landa_p = l

                    if landa_p:
                        # If landa_p exists
                        U.append((T_p.id, landa_p))

                if len(U) > 1:
                    logging.debug(f'\t\tCluster {c} swapping {U}')
                    # Randomly swap all triples in U
                    random.shuffle(U)
                    for idx, tuple in enumerate(U):
                        anon_trajectories[idx].add_location(tuple[1])

                    # Mark all triples as swapped
                    for tuple in U:
                        trajectory_id = tuple[0]
                        location = tuple[1]
                        triples_swapped.append((trajectory_id, location.timestamp, location.x, location.y))

            # Build anonymized dataset
            for T in anon_trajectories:
                # Sort by timestamp
                T.locations.sort(key=lambda x: x.timestamp)
                self.anonymized_dataset.add_trajectory(T)

            logging.debug(f'\tCluster {c} processed!')

        logging.info(f'{len(triples_swapped)} triples swapped!')

        self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]
        logging.info("Removed trajectories with less than 1 locations!\n")

        logging.info("Done!\n")


    def get_anonymized_dataset(self):
        return self.anonymized_dataset
