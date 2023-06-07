import unittest

import geopandas.testing
import shapely
from geopandas import GeoDataFrame
from skmob.utils.constants import DEFAULT_CRS

from entities.Dataset import Dataset
from tests.TestBase import TestBase


class TestDataset(TestBase):
    def setUp(self):
        super().setUp()

    def test_load_dataset(self):
        dataset = Dataset()
        with self.assertRaises(FileNotFoundError):
            dataset.from_file("not_found.csv")

        with self.assertRaises(TypeError):
            dataset.from_file("Format_not.supported")

        dataset.from_file("../examples/data/mock_dataset.csv")

        self.assertEqual(len(dataset), 46)
        self.assertEqual(dataset.get_number_of_locations(), 383)
        self.assertEqual(dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(dataset.get_max_timestamp(), 1669058195)
        self.assertEqual(dataset.get_n_locations_longest_trajectory(), 28)

        point_list = [[1.27465, 41.14071], [1.27465, 41.10911], [1.23216, 41.10911], [1.23216, 41.14071]]
        poly = shapely.geometry.Polygon(point_list)
        geodf = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[poly])
        geopandas.testing.assert_geodataframe_equal(dataset.get_bounding_box(), geodf)

    def test_filter(self):
        dataset = Dataset()
        dataset.from_file("../examples/data/mock_dataset.csv")

        dataset.filter_by_speed(10)

        self.assertEqual(len(dataset), 41)
        self.assertEqual(dataset.get_number_of_locations(), 331)
        self.assertEqual(dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(dataset.get_max_timestamp(), 1669056327)
        self.assertEqual(dataset.get_n_locations_longest_trajectory(), 28)

        dataset.filter_by_n_locations(10)

        self.assertEqual(len(dataset), 7)
        self.assertEqual(dataset.get_number_of_locations(), 104)
        self.assertEqual(dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(dataset.get_max_timestamp(), 1669056327)
        self.assertEqual(dataset.get_n_locations_longest_trajectory(), 28)

        dataset.filter_by_length(min_length=3, max_length=10)

        self.assertEqual(len(dataset), 3)
        self.assertEqual(dataset.get_number_of_locations(), 43)
        self.assertEqual(dataset.get_min_timestamp(), 1669043011)
        self.assertEqual(dataset.get_max_timestamp(), 1669053074)
        self.assertEqual(dataset.get_n_locations_longest_trajectory(), 20)


if __name__ == '__main__':
    unittest.main()
