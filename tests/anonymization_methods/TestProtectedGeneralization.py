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
        method = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 27)
        self.assertEqual(anon_dataset.get_number_of_locations(), 81)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044340)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669058072)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 6)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2435522079467773)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.12770462036133)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044817)

    def test_params(self):
        params = {
            "tile_size": 1000,
            "k": 2,
            "knowledge": 3,
            "strategy": 'centroid'
        }

        method = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 24)
        self.assertEqual(anon_dataset.get_number_of_locations(), 70)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044259)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669049917)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 4)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2591080002029678)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.13955505681732)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669045710)

    def test_time(self):
        params = {
            "tile_size": 500,
            "k": 3,
            "knowledge": 2,
            "strategy": 'avg',
            "time_interval": 60
        }

        method = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 28)
        self.assertEqual(anon_dataset.get_number_of_locations(), 73)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044340)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669047685)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 4)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2420129776000977)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.1143798828125)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044651)

    def test_time_strategy(self):
        params = {
            "tile_size": 500,
            "k": 2,
            "knowledge": 2,
            "strategy": 'centroid',
            "time_interval": 10,
            "time_strategy": 'same'
        }

        method = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        method.run()
        anon_dataset = method.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 35)
        self.assertEqual(anon_dataset.get_number_of_locations(), 96)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044211)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669050811)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 5)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2568622119926687)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.13955505681732)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044211)

    def test_own_tiles(self):
        tiles_filename = f"{TEST_ROOT_DIR}/files/mock_tiles.geojson"

        params = {
            'tiles_filename': tiles_filename
        }

        simple_generalization = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        simple_generalization.run()
        anon_dataset = simple_generalization.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 41)
        self.assertEqual(anon_dataset.get_number_of_locations(), 116)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044225)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669057930)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 5)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2439212799072266)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.115142822265625)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044651)

    def test_own_tiles_time(self):

        tiles_filename = f"{TEST_ROOT_DIR}/files/mock_tiles.geojson"

        params = {
            'tiles_filename': tiles_filename,
            "time_interval": 60
        }

        simple_generalization = AnonymizationMethodFactory.get("ProtectedGeneralization", self.dataset, params)
        simple_generalization.run()
        anon_dataset = simple_generalization.get_anonymized_dataset()

        self.assertEqual(len(anon_dataset), 34)
        self.assertEqual(anon_dataset.get_number_of_locations(), 89)
        self.assertEqual(anon_dataset.get_min_timestamp(), 1669044087)
        self.assertEqual(anon_dataset.get_max_timestamp(), 1669047797)
        self.assertEqual(anon_dataset.get_n_locations_longest_trajectory(), 5)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].x, 1.2438578605651855)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].y, 41.11511993408203)
        self.assertEqual(anon_dataset.trajectories[1].locations[0].timestamp, 1669044651)

if __name__ == '__main__':
    unittest.main()
