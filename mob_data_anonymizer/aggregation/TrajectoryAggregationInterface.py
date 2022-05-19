from abc import abstractmethod

from mob_data_anonymizer.entities.Trajectory import Trajectory


class TrajectoryAggregationInterface:

    @staticmethod
    @abstractmethod
    def compute(self, trajectories: list) -> Trajectory:
        pass
