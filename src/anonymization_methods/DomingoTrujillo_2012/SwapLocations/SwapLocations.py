import logging
import random
from math import sqrt

from src.aggregation.Martinez2021.Aggregation import Aggregation
from src.aggregation.TrajectoryAggregationInterface import TrajectoryAggregationInterface
from src.clustering.ClusteringInterface import ClusteringInterface
from src.clustering.MDAV.SimpleMDAV import SimpleMDAV
from src.clustering.MDAV.SimpleMDAVDataset import SimpleMDAVDataset
from src.distances.DistanceInterface import DistanceInterface
from src.distances.DomingoTrujillo2012.Distance import Distance
from src.entities.Dataset import Dataset
from src.entities.TimestampedLocation import TimestampedLocation
from src.entities.Trajectory import Trajectory


class SwapLocations:
    def __init__(self, dataset: Dataset, k, R_t, R_s, clustering_method: ClusteringInterface = None, distance: DistanceInterface = None, aggregation_method: TrajectoryAggregationInterface = None):
        self.dataset = dataset
        if not distance:
            self.distance = Distance(dataset)
        if not aggregation_method:
            self.aggregation_method = Aggregation
        if not clustering_method:
            mdav_dataset = SimpleMDAVDataset(dataset, self.distance, self.aggregation_method)
            self.clustering_method = SimpleMDAV(mdav_dataset)

        self.anonymized_dataset = dataset.__class__()

        self.k   = k
        self.R_t = R_t
        self.R_s = R_s

    def run(self):

        # Filter dataset. We take just the main component of the distance graph
        filtered_dataset = self.distance.filter_dataset()
        logging.info(f"Dataset filtered by main component. Now it has {len(filtered_dataset)} trajectories.")

        # Clustering
        logging.info("Starting clustering!")
        self.clustering_method.set_dataset(filtered_dataset)
        self.clustering_method.run(self.k)
        logging.info("Clustering finished!")
        logging.debug(self.clustering_method.mdav_dataset.assigned_to)

        logging.info("Swapping locations!")
        clusters = self.clustering_method.get_clusters()

        triples_swapped = []
        for c in clusters:

            cluster_trajectories = clusters[c]

            # Initialize anonymized trajectories
            anon_trajectories = list(map(lambda t: Trajectory(t.id), cluster_trajectories))

            # Let T be a random trajectory in C
            T = random.choice(cluster_trajectories)


            # For all "unswapped" locations in T
            unswapped_locations = [l for l in T.locations if (T.id, l.timestamp, l.x, l.y) not in triples_swapped]
            for landa in unswapped_locations:

                # Initialize U = {landa}
                U = [(T.id, landa)]
                remove_landa = False

                # For all trajectories t_p in C with t_p != T
                for T_p in [traj for traj in cluster_trajectories if traj != T]:
                    # Look for an "unswapped" triple 'l' minimazing the intra-cluster distance in U and such that:
                    d = 99999999
                    landa_p = None
                    for l in T_p.locations:
                        # If triple has not been swapped
                        if (T_p.id, l.timestamp, l.x, l.y) not in triples_swapped:
                            if abs(l.timestamp - landa.timestamp) <= self.R_t:

                                d_s = sqrt((l.x - landa.x) ** 2 + (l.y - landa.y) ** 2)

                                if 0 <= d_s <= self.R_s:
                                    # We take the location with the minimum intra-cluster distance
                                    if TimestampedLocation.compute_centroid([tuple[1] for tuple in U]).distance(l) < d:
                                        d = landa.distance(l)
                                        landa_p = l

                    if landa_p:
                        # If landa_p exists
                        U.append((T_p.id, landa_p))
                    else:
                        # Remove landa -> We don't include 'landa' in anonymized trajectory
                        remove_landa = True
            
                if not remove_landa:

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
        logging.info("Done!\n")
        logging.info('Anonymization finished!')

    def get_anonymized_dataset(self):
        return self.anonymized_dataset


