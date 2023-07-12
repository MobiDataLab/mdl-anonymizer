import unittest

from entities.Dataset import Dataset
from factories.measures_method_factory import MeasuresMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestRecordLinkage(TestBase):

    def setUp(self):

        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

        self.a_dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset_anonymized.csv"
        self.a_dataset.from_file(path)

    def test_default(self):

        measure = MeasuresMethodFactory.get('RecordLinkage', self.dataset, self.a_dataset, {'seed': 20})
        measure.run()
        result = measure.get_result()

        self.assertEqual(result['percen_record_linkage'], 28.26)
        # self.assertEqual(result['percen_record_linkage_sample'], 28.26)


if __name__ == '__main__':
    unittest.main()
