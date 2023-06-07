import unittest

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnonymizationMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestMicroAggregation(TestBase):

    def setUp(self):
        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

    def test_default(self):
        method = AnonymizationMethodFactory.get("Microaggregation", self.dataset)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 387)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044256)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669051521)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 14)

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
                    'name': 'Mean_trajectory'
                }
            },
            'aggregation_method': {
                'name': 'Mean_trajectory'
            }
        }

        swap_locations = AnonymizationMethodFactory.get("Microaggregation", self.dataset, params)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 388)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044914)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669051109)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 12)


if __name__ == '__main__':
    unittest.main()
