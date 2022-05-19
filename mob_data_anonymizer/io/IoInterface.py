from abc import abstractmethod, ABC

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mob_data_anonymizer.entities.Trajectory import Trajectory


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


