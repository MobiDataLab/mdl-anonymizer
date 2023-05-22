import unittest

import geopandas.testing
import shapely
from geopandas import GeoDataFrame
from skmob.utils.constants import DEFAULT_CRS

from entities.Dataset import Dataset


class TestDataset(unittest.TestCase):

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
        self.assertEqual(dataset.get_max_trajectory_length(), 28)

        point_list = [[1.27465, 41.14071], [1.27465, 41.10911], [1.23216, 41.10911], [1.23216, 41.14071]]
        poly = shapely.geometry.Polygon(point_list)
        geodf = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[poly])
        geopandas.testing.assert_geodataframe_equal(dataset.get_bounding_box(), geodf)



if __name__ == '__main__':
    unittest.main()