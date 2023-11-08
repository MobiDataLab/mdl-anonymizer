from random import randint
import sys

from mdl_anonymizer.aggregation.TrajectoryAggregationInterface import TrajectoryAggregationInterface
from mdl_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mdl_anonymizer.entities.Trajectory import Trajectory


class Closest_locations_to_mean_trajectory(TrajectoryAggregationInterface):

    def __init__(self, p_lambda: float):
        self.p_lambda = p_lambda

    def compute(self, trajectories: list) -> Trajectory:

        # Avg of trajectories length
        len_avgs = [len(t) for t in trajectories]
        centroid_length = round(sum(len_avgs) / len(trajectories))

        # Length ratio
        gaps = list(map(lambda t: round(len(t) / centroid_length, 2), trajectories))

        aggregated_locations = []
        temp_locations = []
        indexes = [0.0] * len(trajectories)
        for i in range(0, centroid_length):
            # Gathering the corresponding location of every trajectory
            for idx, t in enumerate(trajectories):
                index = int(indexes[idx])
                if index >= len(t):
                    index = len(t) - 1
                temp_locations.append(t.locations[index])

            # Compute locations centroid
            aggregated_locations.append(TimestampedLocation.compute_centroid(temp_locations))
            temp_locations = []

            # Compute new indexes
            indexes = [x + y for x, y in zip(indexes, gaps)]

        # Search the closest real locations to the centroid trajectory
        min_locations = []
        for aggregated_location in aggregated_locations:
            min_dist = float('inf')
            min_location = aggregated_location
            for trajectory in trajectories:
                for location in trajectory.locations:
                    dist = aggregated_location.distance_weighted(location, self.p_lambda)
                    if dist < min_dist:
                        min_dist = dist
                        min_location = location
            min_locations.append(min_location)

        aggregated_trajectory = Trajectory("C_"+str(randint(0, 10000)))
        aggregated_trajectory.add_locations(min_locations)

        return aggregated_trajectory
