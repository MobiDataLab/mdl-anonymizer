import logging
import unittest

from src.anonymization_methods.DomingoTrujillo_2012.SwapLocations.SwapLocations import SwapLocations
from src.utils.Stats import Stats
from examples.anonymize.src.entities.CabDatasetTXT import CabDatasetTXT


class TestSwapLocations(unittest.TestCase):
    def test_something(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO)

        dataset = CabDatasetTXT()
        # dataset.load("../../data/TXT_SF_Cabs", n_trajectories=50, n_locations=500)
        dataset.load_from_scikit('../../data/cabs_dataset_20080608.csv', n_trajectories=100, datetime_key="timestamp")
        dataset.filter()
        # self.assertEqual(10, len(dataset))

        # print(dataset)

        swap_locations = SwapLocations(dataset, k=3, R_t=180, R_s=1)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()
        anon_dataset.set_description("ANONYMIZED DATASET")

        anon_dataset.export_to_scikit(filename="../../out/cabs_scikit_anonymized.csv")

        # print(anon_dataset)

        stats = Stats(dataset, anon_dataset)
        print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
        print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')



if __name__ == '__main__':
    unittest.main()
