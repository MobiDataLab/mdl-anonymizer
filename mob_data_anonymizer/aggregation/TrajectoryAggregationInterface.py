from abc import abstractmethod

from mob_data_anonymizer.entities.Trajectory import Trajectory


class TrajectoryAggregationInterface:

    @staticmethod
    @abstractmethod
    def compute(trajectories: list) -> Trajectory:
        pass
