import unittest

from mob_data_anonymizer.aggregation.Martinez2021.Aggregation import Aggregation
from mob_data_anonymizer.tests.build_mocks import get_mock_dataset


class TestAggregation(unittest.TestCase):
    def test(self):

        dataset = get_mock_dataset()

        trajectory = Aggregation.compute(dataset.trajectories)

        # print(trajectory)

        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
