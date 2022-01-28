from src.entities.TimestampedLocation import TimestampedLocation
from src.entities.Trajectory import Trajectory
from examples.anonymize.src.entities.CabDatasetTXT import CabDatasetTXT

trajectories = [
    [[100, 0, 0], [105, 5, 5], [110, 7, 10], [115, 3, 17], [120, 5, 21], [125, 10, 20]],
    [[0, 5, 5], [3, 8, 6], [5, 8, 8], [10, 7, 10], [13, 10, 6]],
    [[3, 0, 0], [10, 3, 3], [15, 0, 8], [18, 3, 10]],
    [[5, 0, 3], [8, 2, 4], [10, 3, 8], [13, 5, 10], [15, 8, 12], [20, 5, 10], [25, 3, 12], [28, 0, 15], [30, 2, 17]],
    [[10, 20, 30], [15, 17, 32], [20, 15, 34], [23, 12, 37], [27, 10, 40]],
    [[20, 10, 15], [25, 7, 12], [30, 3, 7], [35, 0, 3], [40, 0, 0]],
    [[20, 0, 30], [25, 2, 27], [30, 5, 22], [35, 8, 17], [40, 12, 22], [43, 15, 25], [46, 12, 28]],
    [[30, 0, 6], [32, 1, 7], [35, 3, 7], [40, 5, 10], [45, 10, 11], [50, 12, 15]],
    [[25, 0, 0], [32, 5, 5], [35, 7, 10], [40, 3, 17], [45, 5, 21], [50, 10, 20]],
    [[0, 0, 0], [5, 5, 5], [10, 7, 10]],
    [[8, 5, 5], [20, 8, 6], [25, 8, 8]],
    [[20, 10, 15], [25, 7, 12], [30, 3, 7]]
]


def get_mock_dataset():
    dataset = CabDatasetTXT()

    trajectories_2 = [
        [[0, 0, 0], [5, 5, 5], [10, 7, 10], [15, 3, 17], [20, 5, 21], [25, 10, 20]],
        [[0, 5, 5], [3, 8, 6], [5, 8, 8], [10, 7, 10], [13, 10, 6]],
        [[3, 0, 0], [10, 3, 3], [15, 0, 8], [18, 3, 10]],
        [[20, 10, 15], [25, 7, 12], [30, 3, 7], [35, 0, 3], [40, 0, 0]],
        [[30, 0, 6], [32, 1, 7], [35, 3, 7], [40, 5, 10], [45, 10, 11], [50, 12, 15]],
    ]

    for idx, t in enumerate(trajectories_2):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset


def get_mock_dataset_2():
    dataset = CabDatasetTXT()

    trajectories_3 = [
        [[0, 0, 0], [5, 5, 5], [10, 7, 10]],
        [[8, 5, 5], [20, 8, 6], [25, 8, 8]],
        [[20, 10, 15], [25, 7, 12], [30, 3, 7]],
    ]

    for idx, t in enumerate(trajectories_3):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset

def get_mock_dataset_3():
    dataset = CabDatasetTXT()

    trajectories_3 = [
        [[0, 0, 0], [5, 5, 5], [10, 10, 10]],
        [[0, 5, 5], [5, 10, 10], [10, 15, 15]],
        [[0, 10, 10], [5, 15, 15], [10, 20, 20]],
    ]

    for idx, t in enumerate(trajectories_3):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset

def get_mock_dataset_4():
    dataset = CabDatasetTXT()

    trajectories_4 = [
        [[0, 0, 0], [5, 5, 5], [10, 10, 10]],
        [[5, 5, 5], [10, 10, 10], [15, 15, 15]],
        [[10, 10, 10], [15, 15, 15], [20, 20, 20]],
    ]

    for idx, t in enumerate(trajectories_4):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset

def get_mock_dataset_5():
    dataset = CabDatasetTXT()

    trajectories_4 = [
        [[0, 0, 0], [10, 5, 5], [25, 10, 10]],
        [[0, 5, 5], [15, 10, 10], [25, 15, 15]],
        [[0, 10, 10], [20, 15, 15], [25, 20, 20]],
    ]

    for idx, t in enumerate(trajectories_4):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset

def get_mock_dataset_6():
    dataset = CabDatasetTXT()

    trajectories_6 = [
        [[0, 0, 0], [5, 5, 5], [10, 7, 10], [15, 3, 17], [20, 5, 21], [25, 10, 20]],
        [[20, 10, 15], [25, 7, 12], [30, 3, 7], [35, 0, 3], [40, 0, 0]],
        [[20, 0, 30], [25, 2, 27], [30, 5, 22], [35, 8, 17], [40, 12, 22], [43, 15, 25], [46, 12, 28]],
    ]

    for idx, t in enumerate(trajectories_6):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset

def get_mock_dataset_7():
    dataset = CabDatasetTXT()

    trajectories_6 = [
        [[0, 0, 0], [5, 5, 5], [10, 7, 10], [15, 3, 17], [20, 5, 21], [25, 10, 20]],
        [[20, 10, 15], [25, 7, 12], [30, 3, 7], [35, 0, 3], [40, 0, 0]],
        [[20, 0, 30], [25, 2, 27], [30, 5, 22], [35, 8, 17], [40, 12, 22], [43, 15, 25], [46, 12, 28]],
        [[50, 0, 30], [55, 2, 27], [60, 5, 22]],
    ]

    for idx, t in enumerate(trajectories_6):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset

def get_mock_dataset_8():
    dataset = CabDatasetTXT()

    trajectories_6 = [
        [[0, 0, 0], [5, 5, 5], [8, 15, 5]],
        [[1, 0, 0], [5, 5, 5], [10, 7, 10], [15, 3, 17], [20, 5, 21], [25, 10, 20]],
    ]

    for idx, t in enumerate(trajectories_6):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset

def get_mock_dataset_N(num):
    dataset = CabDatasetTXT()
    dataset.set_description("TEST DATASET")

    trajs = trajectories[0:num]

    for idx, t in enumerate(trajs):
        trajectory = Trajectory(idx)
        for l in t:
            trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))
        dataset.add_trajectory(trajectory)

    return dataset


def get_mock_trajectory_1():
    t = [[0, 0, 0], [5, 5, 5]]

    trajectory = Trajectory(0)
    for l in t:
        trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))

    return trajectory

def get_mock_trajectory_2():
    t = [[0, 0, 0], [5, 5, 5], [10, 7, 10], [15, 3, 17], [20, 5, 21], [25, 10, 20]]

    trajectory = Trajectory(0)
    for l in t:
        trajectory.add_location(TimestampedLocation(l[0], l[1], l[2]))

    return trajectory
