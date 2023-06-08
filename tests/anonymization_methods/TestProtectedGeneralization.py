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
        self.assertEqual(anon_dataset.get_number_of_locations(), 51)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669045090)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058072)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 3)

    def test_params(self):

        params = {
            "tile_size": 1000,
            "k": 2,
            "knowledge": 3
        }

        swap_locations = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        swap_locations.run()
        anon_dataset = swap_locations.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 29)
        self.assertEqual(anon_dataset.get_number_of_locations(), 96)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044340)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058072)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 6)


if __name__ == '__main__':
    unittest.main()
