from abc import abstractmethod, ABC

from src.entities.Dataset import Dataset
from src.entities.TimestampedLocation import TimestampedLocation
from src.entities.Trajectory import Trajectory


class IoInterface(ABC):

    @staticmethod
    @abstractmethod
    def export_dataset(self, dataset: Dataset) -> list:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def export_trajectory(self, trajectory: Trajectory) -> list:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def export_location(self, location: TimestampedLocation) -> list:
        raise NotImplementedError


