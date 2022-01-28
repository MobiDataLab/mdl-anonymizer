import itertools
import unittest

from src.distances.trajectory.IdeaFeliz2021.Distance import Distance
from src.tests.build_mocks import get_mock_dataset_8, get_mock_dataset_N


class MyTestCase(unittest.TestCase):

    def test_distance(self):
        dataset = get_mock_dataset_N(10)

        distance = Distance(dataset, landa=1)

        for t1, t2 in itertools.combinations(dataset.trajectories, 2):
            d = distance.compute(t1, t2)
            print(f'{t1.id}-{t2.id}: {d}')

        #self.assertEqual(2.65915, round(d, 5))

    def test_distance2(self):
        dataset = get_mock_dataset_N(10)

        distance = Distance(dataset, landa=1)

        t1 = dataset.trajectories[4]
        t2 = dataset.trajectories[8]

        d = distance.compute(t1, t2)
        print(f'{t1.id}-{t2.id}: {d}')

        #self.assertEqual(2.65915, round(d, 5))


if __name__ == '__main__':
    unittest.main()
