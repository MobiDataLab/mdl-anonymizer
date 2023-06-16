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

        self.assertEqual(len(anon_dataset), 26)
        self.assertEqual(anon_dataset.get_number_of_locations(), 64)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044506)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058072)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 4)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.243343710899353)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.12770080566406)

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

        self.assertEqual(len(anon_dataset), 30)
        self.assertEqual(anon_dataset.get_number_of_locations(), 100)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043570)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669053213)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 6)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 41.13955)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 1.25911)


if __name__ == '__main__':
    unittest.main()
