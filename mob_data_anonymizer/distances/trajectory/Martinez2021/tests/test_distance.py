import unittest

from definitions import ROOT_DIR
from mob_data_anonymizer.distances.trajectory.Martinez2021.Distance import Distance
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.tests.build_mocks import get_mock_dataset_3, get_mock_dataset_6, get_mock_dataset_8


class MyTestCase(unittest.TestCase):

    def test_computing_landa(self):
        dataset = get_mock_dataset_3()

        distance = Distance(dataset, sp_type='Euclidean')

        self.assertEqual(2.000005037969036, distance.landa)

    def test_distance(self):
        dataset = get_mock_dataset_8()

        distance = Distance(dataset, sp_type='Euclidean')

        t1 = dataset.trajectories[0]
        t2 = dataset.trajectories[1]

        d = distance.compute(t1, t2)

        self.assertEqual(2.65915, round(d,5))


if __name__ == '__main__':
    unittest.main()
