import unittest

from entities.Dataset import Dataset
from factories.measures_method_factory import MeasuresMethodFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestTrajectoriesRemoved(TestBase):

    def setUp(self):

        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

        self.a_dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset_anonymized.csv"
        self.a_dataset.from_file(path)

    def test_default(self):

        measure = MeasuresMethodFactory.get('TrajectoriesRemoved', self.dataset, self.a_dataset)
        measure.run()
        result = measure.get_result()

        self.assertEqual(result['percen_traj_removed'], 0.0)
        self.assertEqual(result['percen_loc_removed'], -1.04)


if __name__ == '__main__':
    unittest.main()
