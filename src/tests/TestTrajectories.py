import logging
import time
import unittest

from src.tests.build_mocks import get_mock_trajectory
from use_package.src.entities.CabDatasetTXT import CabDatasetTXT


class TestTrajectories(unittest.TestCase):
    def test(self):
        traj = get_mock_trajectory()

        loc1 = traj.get_location_by_timestamp(10)
        self.assertEqual(loc1.get_list(), [10, 7, 10])

    def test2(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.DEBUG)

        dataset = CabDatasetTXT()
        dataset.load("../../use_package/data/TXT_SF_Cabs", n_trajectories=50, n_locations=500)
        # print(dataset)
        traj = dataset.get_trajectory("enyenewl")

        start = time.time_ns()

        loc_1 = traj.get_location_by_timestamp(1212948166)
        loc_2 = traj.get_location_by_timestamp(1212947292)
        ot = (1212948166, 1212947292)
        d = (pow(loc_1.x - loc_2.x, 2) + pow(loc_1.y - loc_2.y, 2)) / pow(max(ot) - min(ot), 2)
        print(f'time: {time.time_ns() - start}')
        print(d)


    def test3(self):
        traj = get_mock_trajectory()

        loc3 = traj.get_next_location_by_timestamp(12)
        self.assertEqual(loc3.get_list(), [15, 3, 17], "When timestamp DOES NOT exist")

        loc3 = traj.get_next_location_by_timestamp(15)
        self.assertEqual(loc3.get_list(), [20, 5, 21], "When timestamp exists")

    def test4(self):
        traj = get_mock_trajectory()

        ts = traj.get_interval_timestamps((5, 15))
        self.assertEqual([5, 10, 15], ts)

        ts = traj.get_interval_timestamps((3, 12))
        self.assertEqual([5, 10], ts)

        ts = traj.get_interval_timestamps((0, 100))
        self.assertEqual([0, 5, 10, 15, 20, 25], ts)

if __name__ == '__main__':
    unittest.main()
