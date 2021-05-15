from abc import abstractmethod

from src.entities.Trajectory import Trajectory


class TrajectoryAggregationInterface:

    @staticmethod
    @abstractmethod
    def compute(self, trajectories: list) -> Trajectory:
        pass
