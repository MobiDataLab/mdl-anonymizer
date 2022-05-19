from abc import abstractmethod, ABC

from mob_data_anonymizer.entities.Trajectory import Trajectory


class DistanceInterface(ABC):
    @abstractmethod
    def compute(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        raise NotImplementedError

    @abstractmethod
    def filter_dataset(self):
        raise NotImplementedError
