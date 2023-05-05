from mob_data_anonymizer.aggregation.Martinez2021.Aggregation import Aggregation
from mob_data_anonymizer.aggregation.TrajectoryAggregationInterface import TrajectoryAggregationInterface
from mob_data_anonymizer.clustering.MDAV.interfaces.MDAVDatasetInterface import MDAVDatasetInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory
from mob_data_anonymizer.distances.trajectory.DistanceInterface import DistanceInterface
import numpy as np


class SimpleMDAVDataset(MDAVDatasetInterface):

    def __init__(self, dataset: Dataset, distance: DistanceInterface,
                 aggregation_method: TrajectoryAggregationInterface = None):
        self.dataset = dataset
        self.distance = distance
        self.trajectories_elegible = np.array(self.dataset.trajectories)
        self.distances = None
        self.unselected_len = len(dataset)
        self.assigned_to = {}                             # Cluster assigned to every trajectory
        self.cluster_id = 0
        if not aggregation_method:
            self.aggregation_method = Aggregation
        else:
            self.aggregation_method = aggregation_method

    def set_dataset(self, dataset: Dataset):
        self.dataset = dataset
        self.trajectories_elegible = np.array(self.dataset.trajectories)
        self.unselected_len = len(dataset)
        self.assigned_to = {}
        self.cluster_id = 0

    def reset(self):
        self.unselected_len = len(self.dataset)
        self.assigned_to = {}                        # Cluster assigned to every trajectory
        self.cluster_id = 0

    def compute_centroid(self):
        return self.aggregation_method.compute(self.dataset.trajectories)

    def compute_centroid_unselected(self):
        # Collect unselected trajectories
        raise NotImplementedError

    def make_cluster(self, traj: Trajectory, k):
        self.trajectories_elegible = self.trajectories_elegible[np.argpartition(self.distances, k-1)]
        closest = [traj]
        closest.extend(self.trajectories_elegible[:k-1])
        self.trajectories_elegible = self.trajectories_elegible[k-1:]

        for t in closest:
            self.assigned_to[t.index] = self.cluster_id
        self.cluster_id += 1

    def make_cluster_unselected(self):
        for t in self.trajectories_elegible:
            self.assigned_to[t.index] = self.cluster_id
        self.cluster_id += 1

    def farthest_from(self, traj: Trajectory):
        self.calculate_distances(traj)
        index = np.argmax(self.distances)
        farthest = self.trajectories_elegible[index]
        self.trajectories_elegible = np.delete(self.trajectories_elegible, index)

        return farthest, index

    def calculate_distances(self, traj: Trajectory):
        self.distances = [self.distance.compute(traj, t) for t in self.trajectories_elegible]

    def unselected_length(self):
        return len(self.trajectories_elegible)

    def get_num_clusters(self):
        return self.cluster_id

    def __len__(self):
        return len(self.dataset.trajectories)