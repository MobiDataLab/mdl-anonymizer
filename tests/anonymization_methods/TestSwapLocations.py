import unittest

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnonymizationMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestSwapLocations(TestBase):

    def setUp(self):
        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

    def test_default(self):

        swap_locations = AnonymizationMethodFactory.get("SwapLocations", self.dataset, {'seed': 42})
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 35)
        self.assertEqual(anon_dataset.get_number_of_locations(), 166)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044573)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669048073)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 8)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2393100261688232)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.117374420166016)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044682)


    def test_params(self):

        params = {
            "k": 4,
            "max_r_s": 400,
            "min_r_s": 100,
            "max_r_t": 300,
            "min_r_t": 60,
            "tile_size": 1500,
            'seed': 23
        }

        swap_locations = AnonymizationMethodFactory.get("SwapLocations", self.dataset, params)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 38)
        self.assertEqual(anon_dataset.get_number_of_locations(), 146)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044651)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669048450)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 9)


if __name__ == '__main__':
    unittest.main()
