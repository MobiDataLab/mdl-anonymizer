import logging
import unittest

from mob_data_anonymizer.anonymization_methods.DomingoTrujillo_2012.SwapLocations.SwapLocations import SwapLocations
from mob_data_anonymizer.tests.build_mocks import get_mock_dataset_N
from mob_data_anonymizer.utils.Stats import Stats


class TestSwapLocations(unittest.TestCase):
    def test_mock(self):

        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.DEBUG)

        dataset = get_mock_dataset_N(9)
        logging.debug(dataset)

        swap_locations = SwapLocations(dataset, k=3, R_t=25, R_s=30)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()
        anon_dataset.set_description("ANONYMIZED DATASET")
        logging.debug(anon_dataset)

        stats = Stats(dataset, anon_dataset)
        print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
        print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')


if __name__ == '__main__':
    unittest.main()
