import unittest

import geopandas.testing
import shapely
from geopandas import GeoDataFrame
from skmob.utils.constants import DEFAULT_CRS

from entities.Dataset import Dataset
from mob_data_anonymizer.factories.analysis_method_factory import AnalysisMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestQuadTreeHeatMap(TestBase):

    def setUp(self):

        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

    def test_default(self):

        method = AnalysisMethodFactory.get('QuadTreeHeatMap', self.dataset, {})
        method.run()
        result = method.get_result()

        right_P = shapely.wkt.loads('POLYGON((1.2534032695145003 41.12490951149509, 1.2534032695145003 41.132811329826694, '
                              '1.27464798381945 41.132811329826694, 1.27464798381945 41.12490951149509, '
                              '1.2534032695145003 41.12490951149509))')

        right_geodf = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[right_P])

        computed_P = result['geometry'][0]
        computed_geodf = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[computed_P])

        geopandas.testing.assert_geodataframe_equal(computed_geodf, right_geodf)


    def test_params(self):

        params = {
            "min_k": 3,
            "min_sector_length": 200,
            "merge_sectors": False
        }

        method = AnalysisMethodFactory.get('QuadTreeHeatMap', self.dataset, params)
        method.run()
        result = method.get_result()

        right_P = shapely.wkt.loads('POLYGON ((1.2374697337857876 41.109105874831904, 1.2374697337857876 '
                                    '41.1130567839977, 1.2427809123620253 41.1130567839977, 1.2427809123620253 '
                                    '41.109105874831904, 1.2374697337857876 41.109105874831904))')

        right_geodf = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[right_P])

        computed_P = result['geometry'][0]
        computed_geodf = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[computed_P])

        geopandas.testing.assert_geodataframe_equal(computed_geodf, right_geodf)

if __name__ == '__main__':
    unittest.main()
