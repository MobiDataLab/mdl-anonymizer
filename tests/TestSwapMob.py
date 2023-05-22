import logging
import unittest

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnoymizationMethodFactory


class TestSwapMob(unittest.TestCase):

    def setUp(self):
        self.dataset = Dataset()
        self.dataset.from_file("../examples/data/mock_dataset.csv")

    def test_default(self):

        # logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
        #                     level=logging.DEBUG)

        swap_locations = AnoymizationMethodFactory.get("SwapMob", self.dataset, {'seed': 23})
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 28)
        self.assertEqual(anon_dataset.get_number_of_locations(), 260)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043570)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669056327)
        self.assertEqual(anon_dataset.get_max_trajectory_length(), 25)

    def test_params(self):
        params = {
            'spatial_thold': 0.1,
            'temporal_thold': 60,
            'min_n_swaps': 2,
            'seed': 47
        }

        swap_locations = AnoymizationMethodFactory.get("SwapMob", self.dataset, params)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 4)
        self.assertEqual(anon_dataset.get_number_of_locations(), 37)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044361)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669048131)
        self.assertEqual(anon_dataset.get_max_trajectory_length(), 12)


if __name__ == '__main__':
    unittest.main()
