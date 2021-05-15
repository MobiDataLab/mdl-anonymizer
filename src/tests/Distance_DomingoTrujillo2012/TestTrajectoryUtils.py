import unittest

from src.distances.DomingoTrujillo2012.DistanceGraph import DistanceGraph
from src.distances.DomingoTrujillo2012.TrajectoryUtils import get_p_contemporary, get_overlap_time
from src.tests.build_mocks import get_mock_dataset, get_mock_dataset_2


class TestTrajectoryUtils(unittest.TestCase):

    def test_mock_dataset(self):
        dataset = get_mock_dataset()

        self.assertEqual(len(dataset.trajectories), 5)

    def test_p_contemporary_1(self):
        dataset = get_mock_dataset()

        traj_0 = dataset.get_trajectory(0)
        traj_1 = dataset.get_trajectory(1)
        traj_2 = dataset.get_trajectory(2)
        traj_3 = dataset.get_trajectory(3)
        traj_4 = dataset.get_trajectory(4)

        p = get_p_contemporary(traj_0, traj_4)
        self.assertEqual(p, 0.0, "0-4")

        p = get_p_contemporary(traj_3, traj_4)
        self.assertEqual(p, 0.0, "3-4")

        p = get_p_contemporary(traj_0, traj_1)
        self.assertEqual(p, 52, "0-1")

        p = get_p_contemporary(traj_1, traj_2)
        self.assertEqual(p, 66.67, "1-2")

    def test_p_contemporary_2(self):
        dataset = get_mock_dataset_2()

        traj_0 = dataset.get_trajectory(0)
        traj_1 = dataset.get_trajectory(1)
        traj_2 = dataset.get_trajectory(2)

        p = get_p_contemporary(traj_0, traj_2)
        self.assertEqual(p, 0.0, "0-2")

        p = get_p_contemporary(traj_0, traj_1)
        self.assertEqual(p, 11.76, "0-1")

        p = get_p_contemporary(traj_1, traj_2)
        self.assertEqual(p, 29.41, "1-2")

    def test_overlap_time_2(self):
        dataset = get_mock_dataset_2()

        traj_0 = dataset.get_trajectory(0)
        traj_1 = dataset.get_trajectory(1)
        traj_2 = dataset.get_trajectory(2)

        ot = get_overlap_time(traj_0, traj_2)
        self.assertEqual(None, ot, "0-1")

        ot = get_overlap_time(traj_0, traj_1)
        self.assertEqual((8, 10), ot, "0-1")

        ot = get_overlap_time(traj_1, traj_2)
        self.assertEqual((20, 25), ot, "1-2")




if __name__ == '__main__':
    unittest.main()
