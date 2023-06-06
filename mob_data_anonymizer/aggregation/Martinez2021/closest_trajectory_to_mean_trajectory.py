from random import randint

from mob_data_anonymizer.aggregation.TrajectoryAggregationInterface import TrajectoryAggregationInterface
from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mob_data_anonymizer.entities.Trajectory import Trajectory


class Closest_trajectory_to_mean_trajectory(TrajectoryAggregationInterface):

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

        centroid_trajectory = Trajectory("C_" + str(randint(0, 10000)))
        centroid_trajectory.add_locations(aggregated_locations)

        # Search the closest real trajectory to the centroid trajectory
        min_trajectory = trajectories[0]
        min_dist = float('inf')
        for trajectory in trajectories:
            dist = centroid_trajectory.default_distance(trajectory, self.p_lambda)
            if dist < min_dist:
                min_dist = dist
                min_trajectory = trajectory

        aggregated_trajectory = Trajectory("C_" + str(randint(0, 10000)))
        aggregated_trajectory.add_locations(min_trajectory.locations)

        return aggregated_trajectory
