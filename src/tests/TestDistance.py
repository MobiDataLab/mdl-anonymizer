import unittest

from src.distances.DomingoTrujillo2012.Distance import Distance
from src.tests.build_mocks import get_mock_dataset


class TestDistance(unittest.TestCase):

    def test_something(self):
        dataset = get_mock_dataset()

        traj_0 = dataset.get_trajectory(0)
        traj_1 = dataset.get_trajectory(1)
        traj_2 = dataset.get_trajectory(2)
        traj_3 = dataset.get_trajectory(3)
        traj_4 = dataset.get_trajectory(4)

        distance = Distance(dataset)

        # Two trajectories not linked
        d = distance.compute(traj_0, traj_4)
        self.assertEqual(None, d)

        # Two normal trajectories
        d = distance.compute(traj_1, traj_2)
        self.assertEqual(0.02784, d)


if __name__ == '__main__':
    unittest.main()
