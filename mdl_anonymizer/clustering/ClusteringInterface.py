from abc import abstractmethod

from mdl_anonymizer.entities.Trajectory import Trajectory


class ClusteringInterface:
    @abstractmethod
    def run(self, k: int):
        raise NotImplementedError

    def get_clusters(self) -> list:
        raise NotImplementedError
