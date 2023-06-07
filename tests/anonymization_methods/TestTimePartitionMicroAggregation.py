import unittest

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.factories.anonymization_method_factory import AnonymizationMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestTimePartitionMicroAggregation(TestBase):

    def setUp(self):
        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

    def test_default(self):

        method = AnonymizationMethodFactory.get("TimePartMicroaggregation", self.dataset)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 382)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043640)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669052037)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 14)

    def test_params(self):
        params = {
            'k': 5,
            'interval': 600,
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

        method = AnonymizationMethodFactory.get("TimePartMicroaggregation", self.dataset, params)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 394)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043928)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669050490)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 15)


if __name__ == '__main__':
    unittest.main()
