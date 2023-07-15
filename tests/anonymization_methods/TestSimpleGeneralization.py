import unittest

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnonymizationMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestSimpleGeneralization(TestBase):

    def setUp(self):
        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

    def test_default(self):

        simple_generalization = AnonymizationMethodFactory.get("SimpleGeneralization", self.dataset)
        simple_generalization.run()
        anon_dataset = simple_generalization.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 383)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058195)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 28)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2388959063102787)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.11418028778517)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044651)

    def test_params(self):

        params = {
            "tile_size": 250,
            "overlapping_strategy": "one"
        }

        simple_generalization = AnonymizationMethodFactory.get("SimpleGeneralization", self.dataset, params)
        simple_generalization.run()
        anon_dataset = simple_generalization.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 364)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058195)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 26)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2400188004154278)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.115026271509265)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044651)

    def test_own_tiles(self):

        tiles_filename = f"{TEST_ROOT_DIR}/files/mock_tiles.geojson"

        params = {
            'tiles_filename': tiles_filename
        }

        simple_generalization = AnonymizationMethodFactory.get("SimpleGeneralization", self.dataset, params)
        simple_generalization.run()
        anon_dataset = simple_generalization.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 46)
        self.assertEqual(anon_dataset.get_number_of_locations(), 383)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058195)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 28)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.242994189976175)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.11441558826653)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044651)


if __name__ == '__main__':
    unittest.main()
