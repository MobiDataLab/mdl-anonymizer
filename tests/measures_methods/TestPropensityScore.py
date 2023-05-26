import unittest

from entities.Dataset import Dataset
from factories.measures_method_factory import MeasuresMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestPropensityScore(TestBase):

    def setUp(self):

        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

        self.a_dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset_anonymized.csv"
        self.a_dataset.from_file(path)

    def test_default(self):

        measure = MeasuresMethodFactory.get('PropensityScore', self.dataset, self.a_dataset, {'seed': 20})
        measure.run()
        result = measure.get_result()

        self.assertEqual(result['propensity'], 0.7252)

    def test_params(self):

        params = {
            'tiles_size': 2000,
            'seed': 20
        }

        measure = MeasuresMethodFactory.get('PropensityScore', self.dataset, self.a_dataset, params)
        measure.run()
        result = measure.get_result()

        self.assertEqual(result['propensity'], 0.2855)


if __name__ == '__main__':
    unittest.main()
