import logging
import unittest

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnoymizationMethodFactory


class TestMicroAggregation(unittest.TestCase):

    def setUp(self):
        self.dataset = Dataset()
        self.dataset.from_file("../examples/data/mock_dataset.csv")

    def test_default(self):

        # logging.basicConfig(format=%(asctime)s %(levelname)-8s %(message)s',
        #                     level=logging.DEBUG)

        method = AnoymizationMethodFactory.get("Microaggregation", self.dataset, {})
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 387)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044256)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669051521)
        self.assertEqual(anon_dataset.get_max_trajectory_length(), 14)

    def test_params(self):
        params = {
            'k': 5,
            'clustering_method': {
                'name': 'SimpleMDAV',
                'params': {
                    'trajectory_distance': {
                        'name': 'Martinez2021'
                    }
                },
                'aggregation_method': {
                    'name': 'Martinez2021'
                }
            },
            'aggregation_method': {
                'name': 'Martinez2021'
            }
        }

        swap_locations = AnoymizationMethodFactory.get("Microaggregation", self.dataset, params)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 388)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044914)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669051109)
        self.assertEqual(anon_dataset.get_max_trajectory_length(), 12)


if __name__ == '__main__':
    unittest.main()
