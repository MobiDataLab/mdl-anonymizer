from abc import abstractmethod

from mdl_anonymizer.entities.Trajectory import Trajectory


class TrajectoryAggregationInterface:

    def compute(self, trajectories: list) -> Trajectory:
        pass
