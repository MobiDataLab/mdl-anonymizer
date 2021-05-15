from abc import abstractmethod, ABC

from src.entities.Trajectory import Trajectory


class DistanceInterface(ABC):
    @abstractmethod
    def compute(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        raise NotImplementedError
