import unittest

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnoymizationMethodFactory
from factories.trajectory_distance_factory import TrajectoryDistanceFactory
from tests import TEST_ROOT_DIR
from tests.TestBase import TestBase


class TestMartinez2021distance(TestBase):

    def setUp(self):
        super().setUp()

        self.dataset = Dataset()
        path = f"{TEST_ROOT_DIR}/../examples/data/mock_dataset.csv"
        self.dataset.from_file(path)

    def test_default(self):
        distance = TrajectoryDistanceFactory.get("Martinez2021", self.dataset, {})
        d = distance.compute(self.dataset.get_trajectory(1), self.dataset.get_trajectory(2))

        self.assertEqual(d, 937.0414983342348)

    def test_lambda(self):
        params = {
            'p_lambda': 0.16,
        }

        distance = TrajectoryDistanceFactory.get("Martinez2021", self.dataset, params)
        d = distance.compute(self.dataset.get_trajectory(3), self.dataset.get_trajectory(4))

        self.assertEqual(d, 2168.2984763410896)

    def test_lambda_max_distance(self):
        params = {
            'p_lambda': 0.16,
            'max_dist': 19865,
            'normalized': True
        }
        distance = TrajectoryDistanceFactory.get("Martinez2021", self.dataset, params)
        d = distance.compute(self.dataset.get_trajectory(1), self.dataset.get_trajectory(2))

        self.assertEqual(d, 0.047126622056823324)

    def test_normalize(self):
        params = {
            'normalized': True,
        }
        distance = TrajectoryDistanceFactory.get("Martinez2021", self.dataset, params)
        d = distance.compute(self.dataset.get_trajectory(1), self.dataset.get_trajectory(2))

        self.assertEqual(d, 0.04716909971646222)


if __name__ == '__main__':
    unittest.main()
