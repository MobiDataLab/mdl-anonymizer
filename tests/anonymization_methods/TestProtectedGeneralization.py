import unittest

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnonymizationMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestProtectedGeneralization(TestBase):

    def setUp(self):
        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

    def test_default(self):

        method = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 27)
        self.assertEqual(anon_dataset.get_number_of_locations(), 81)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044340)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058072)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 6)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2435522079467773)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.12770462036133)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044817)

    def test_params(self):

        params = {
            "tile_size": 1000,
            "k": 2,
            "knowledge": 3,
            "strategy": 'centroid'
        }

        method = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 24)
        self.assertEqual(anon_dataset.get_number_of_locations(), 76)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043570)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669049917)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 4)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 41.13955)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 1.25911)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669045159)

    def test_time(self):
        params = {
            "tile_size": 500,
            "k": 3,
            "knowledge": 2,
            "strategy": 'avg',
            "time_interval": 60
        }

        method = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 28)
        self.assertEqual(anon_dataset.get_number_of_locations(), 73)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044340)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669047685)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 4)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2420129776000977)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.1143798828125)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044651)


if __name__ == '__main__':
    unittest.main()
