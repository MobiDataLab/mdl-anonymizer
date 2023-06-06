from abc import abstractmethod

from mob_data_anonymizer.entities.Trajectory import Trajectory


class TrajectoryAggregationInterface:

    def compute(self, trajectories: list) -> Trajectory:
        pass
