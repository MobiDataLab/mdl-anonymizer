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

        swap_locations = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 21)
        self.assertEqual(anon_dataset.get_number_of_locations(), 54)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044506)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058072)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 4)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2459113597869873)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.12312316894531)

    def test_params(self):

        params = {
            "tile_size": 1000,
            "k": 2,
            "knowledge": 3,
            "strategy": 'centroid'
        }

        swap_locations = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 30)
        self.assertEqual(anon_dataset.get_number_of_locations(), 99)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043945)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669053213)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 6)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.25462)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.13955)


if __name__ == '__main__':
    unittest.main()
