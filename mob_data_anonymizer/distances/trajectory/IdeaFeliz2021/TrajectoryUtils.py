from mob_data_anonymizer.entities.Trajectory import Trajectory


def get_p_contemporary(traj_1: Trajectory, traj_2: Trajectory):
    timestamps_1 = traj_1.get_timestamps()
    timestamps_2 = traj_2.get_timestamps()

    I = max(min(timestamps_1[-1], timestamps_2[-1]) - max(timestamps_1[0], timestamps_2[0]), 0)

    p = 100 * min((I / (timestamps_1[-1] - timestamps_1[0])), (I / (timestamps_2[-1] - timestamps_2[0])))

    return round(p, 2)


def get_overlap_time(traj_1: Trajectory, traj_2: Trajectory):
    timestamps_1 = traj_1.get_timestamps()
    timestamps_2 = traj_2.get_timestamps()

    ts_1 = max(min(timestamps_1), min(timestamps_2))
    ts_2 = min(max(timestamps_1), max(timestamps_2))

    if ts_1 <= ts_2:
        return ts_1, ts_2

    return None
