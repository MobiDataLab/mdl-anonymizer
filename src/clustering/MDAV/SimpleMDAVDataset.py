from src.aggregation.Martinez2021.Aggregation import Aggregation
from src.aggregation.TrajectoryAggregationInterface import TrajectoryAggregationInterface
from src.clustering.MDAV.interfaces.MDAVDatasetInterface import MDAVDatasetInterface
from src.entities.Dataset import Dataset
from src.entities.Trajectory import Trajectory
from src.distances.DistanceInterface import DistanceInterface


class SimpleMDAVDataset(MDAVDatasetInterface):

    def __init__(self, dataset: Dataset, distance: DistanceInterface, aggregation_method: TrajectoryAggregationInterface = None):
        self.dataset = dataset
        self.distance = distance
        self.selected_trajectories = []                   # Ids of trajectories already been clustered
        self.unselected_len = len(dataset)
        self.assigned_to = {}                             # Cluster assigned to every trajectory
        self.cluster_id = 0
        if not aggregation_method:
            self.aggregation_method = Aggregation
        else:
            self.aggregation_method = aggregation_method

    def set_dataset(self, dataset: Dataset):
        self.dataset = dataset
        self.selected_trajectories = []
        self.unselected_len = len(dataset)
        self.assigned_to = {}
        self.cluster_id = 0

    def reset(self):
        self.selected_trajectories = []              # Mark if a trajectory has already been clustered
        self.unselected_len = len(self.dataset)
        self.assigned_to = {}                        # Cluster assigned to every trajectory
        self.cluster_id = 0

    def compute_centroid(self):
        return self.aggregation_method.compute(self.dataset.trajectories)

    def compute_centroid_unselected(self):
        # Collect unselected trajectories
        raise NotImplementedError

    def make_cluster(self, traj: Trajectory, k):
        closest = self.__get_n_closest(traj, k)
        for t_id in closest:
            self.assigned_to[t_id] = self.cluster_id
            self.selected_trajectories.append(t_id)

        self.cluster_id += 1
        self.unselected_len -= k

    def make_cluster_unselected(self):

        unselected_trajectories = [t for idx, t in enumerate(self.dataset.trajectories) if t.id not in self.selected_trajectories]

        for t in unselected_trajectories:
            self.assigned_to[t.id] = self.cluster_id
            self.selected_trajectories.append(t.id)

        self.cluster_id += 1
        self.unselected_len -= len(unselected_trajectories)

    def farthest_from(self, traj: Trajectory) -> Trajectory:

        # Get just unselected trajectories
        unselected_trajectories = [t for idx, t in enumerate(self.dataset.trajectories) if t.id not in self.selected_trajectories]

        max_d = -1
        farthest = None
        for t in unselected_trajectories:
            d = self.distance.compute(traj, t)
            # print(f'Distance {traj.id}-{t.id}: {d}')
            if d and d > max_d:
                max_d = d
                farthest = t

        # print(f'Farthest from {traj.id}: {farthest}. Distance: {max_d}')
        return farthest

    def unselected_length(self):
        return self.unselected_len

    '''
    Return the id of the N closest trajectories (self-included)
    '''
    def __get_n_closest(self, traj: Trajectory, n) -> list:

        # Get just unselected trajectories
        unselected_trajectories = [t for idx, t in enumerate(self.dataset.trajectories) if t.id not in self.selected_trajectories]

        distances = [(t.id, self.distance.compute(traj, t)) for t in unselected_trajectories]

        distances.sort(key=lambda x: x[1])
        closest = distances[:n]

        return [x[0] for x in closest]

    def get_num_clusters(self):
        return self.cluster_id

    def __len__(self):
        return len(self.dataset.trajectories)