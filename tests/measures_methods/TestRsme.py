import unittest

from entities.Dataset import Dataset
from factories.measures_method_factory import MeasuresMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestRsme(TestBase):

    def setUp(self):

        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

        self.a_dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset_anonymized.csv"
        self.a_dataset.from_file(path)

    def test_default(self):

        measure = MeasuresMethodFactory.get('Rsme', self.dataset, self.a_dataset, {})
        measure.run()
        result = measure.get_result()

        self.assertEqual(result['rsme'], 684.7026)


if __name__ == '__main__':
    unittest.main()
