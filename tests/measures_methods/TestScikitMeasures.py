import unittest

from entities.Dataset import Dataset
from factories.measures_method_factory import MeasuresMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestScikitMeasures(TestBase):

    def setUp(self):

        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

        self.a_dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset_anonymized.csv"
        self.a_dataset.from_file(path)

    def test_default(self):

        measure = MeasuresMethodFactory.get('ScikitMeasures', self.dataset, self.a_dataset)
        measure.run()
        result = measure.get_result()

        self.assertEqual(result['visits_per_location_original'], 2.6233)
        self.assertEqual(result['visits_per_location_anonymized'], 4.6627)
        self.assertEqual(result['distance_straight_line_original'], 2.2484)
        self.assertEqual(result['distance_straight_line_anonymized'], 1.7707)
        self.assertEqual(result['uncorrelated_location_entropy_original'], 0.717)
        self.assertEqual(result['uncorrelated_location_entropy_anonymized'], 1.3476)
        self.assertEqual(result['random_location_entropy_original'], 1.0423)
        self.assertEqual(result['random_location_entropy_anonymized'], 1.9491)
        self.assertEqual(result['mean_square_displacement_original'], 2.8363)
        self.assertEqual(result['mean_square_displacement_anonymized'], 1.9704)

if __name__ == '__main__':
    unittest.main()
