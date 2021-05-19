import unittest

from src.clustering.MDAV.SimpleMDAV import SimpleMDAV
from src.clustering.MDAV.SimpleMDAVDataset import SimpleMDAVDataset
from src.distances.trajectory.DomingoTrujillo2012.Distance import Distance
from src.tests.build_mocks import get_mock_dataset_N


class TestSimpleMDAV(unittest.TestCase):
    def test_SimpleMDAV(self):

        dataset = get_mock_dataset_N(6)
        distance = Distance(dataset)
        k = 3

        expected_clusters = int(len(dataset) / k)

        mdav_dataset = SimpleMDAVDataset(dataset, distance)

        mdav = SimpleMDAV(mdav_dataset)

        mdav.run(k)

        print(mdav_dataset.assigned_to)

        actual_clusters = mdav_dataset.get_num_clusters()

        self.assertEqual(actual_clusters, expected_clusters)

        print(distance.compute(4, 5))

        print(distance.distance_graph.graph.edges.data())

        distance.distance_graph.draw_graph()




if __name__ == '__main__':
    unittest.main()
