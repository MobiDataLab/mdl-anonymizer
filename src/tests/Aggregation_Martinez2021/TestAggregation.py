import unittest

from src.aggregation.Martinez2021.Aggregation import Aggregation
from src.tests.build_mocks import get_mock_dataset


class TestAggregation(unittest.TestCase):
    def test(self):

        dataset = get_mock_dataset()

        trajectory = Aggregation.compute(dataset.trajectories)

        # print(trajectory)

        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
