import logging
import unittest

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnoymizationMethodFactory


class TestSimpleGeneralization(unittest.TestCase):

    def setUp(self):
        self.dataset = Dataset()
        self.dataset.from_file("../examples/data/mock_dataset.csv")

    def test_default(self):

        # logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
        #                     level=logging.DEBUG)

        swap_locations = AnoymizationMethodFactory.get("SimpleGeneralization", self.dataset, {})
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 44)
        self.assertEqual(anon_dataset.get_number_of_locations(), 344)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058195)
        self.assertEqual(anon_dataset.get_max_trajectory_length(), 26)

    def test_params(self):

        params = {
            "gen_tile_size": 250,
            "traj_anon_tile_size": 2000,
            "overlapping_strategy": "one"
        }

        swap_locations = AnoymizationMethodFactory.get("SimpleGeneralization", self.dataset, params)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 43)
        self.assertEqual(anon_dataset.get_number_of_locations(), 337)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058195)
        self.assertEqual(anon_dataset.get_max_trajectory_length(), 24)


if __name__ == '__main__':
    unittest.main()
