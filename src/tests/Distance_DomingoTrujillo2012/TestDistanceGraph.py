import unittest

from src.distances.trajectory.DomingoTrujillo2012.Distance import Distance
from src.distances.trajectory.DomingoTrujillo2012.DistanceGraph import DistanceGraph
from src.distances.trajectory.DomingoTrujillo2012.TrajectoryUtils import get_p_contemporary, get_overlap_time
from src.entities.TimestampedLocation import TimestampedLocation
from src.entities.Trajectory import Trajectory
from src.tests.build_mocks import get_mock_dataset, get_mock_dataset_2, get_mock_dataset_3, get_mock_dataset_4, \
    get_mock_dataset_5, get_mock_dataset_N, get_mock_dataset_7


class TestDistanceGraph(unittest.TestCase):

    def test_1(self):
        dataset = get_mock_dataset()

        dg = DistanceGraph(dataset)
        dg.compute()

        d = dg.get_distance(0, 4)
        self.assertEqual(None, d)

        d = dg.get_distance(1, 2)
        self.assertEqual(0.02784, d)

        self.assertEqual(3, dg.graph.number_of_nodes(), "Wrong number of nodes")
        self.assertEqual(4, dg.graph.number_of_edges(), "Wrong number of edges")

        distance = dg.get_graph_distance(1, 2)
        self.assertEqual(0.02784, distance)

    def test_2(self):
        dataset = get_mock_dataset_2()

        dg = DistanceGraph(dataset)
        dg.compute()

        d = dg.get_distance(0, 2)
        self.assertEqual(None, d)

        d = dg.get_distance(1, 2)
        self.assertEqual(0.06868, d)

        self.assertEqual(3, dg.graph.number_of_nodes(), "Wrong number of nodes")
        self.assertEqual(2, dg.graph.number_of_edges(), "Wrong number of edges")

        # dg.draw_graph()
        # distance = dg.get_graph_distance(1, 2)
        # self.assertEqual(0.02784, distance)

    def test_3(self):
        # This dataset has 3 synchronized trajectories
        dataset = get_mock_dataset_3()

        dg = DistanceGraph(dataset)
        dg.compute()

        traj_0 = dataset.get_trajectory(0)
        traj_1 = dataset.get_trajectory(1)
        traj_2 = dataset.get_trajectory(2)

        p1 = get_p_contemporary(traj_0, traj_1)
        self.assertEqual(100, p1)
        p2 = get_p_contemporary(traj_1, traj_2)
        self.assertEqual(100, p2)
        p3 = get_p_contemporary(traj_0, traj_2)
        self.assertEqual(100, p3)

        ot1 = get_overlap_time(traj_0, traj_1)
        self.assertEqual((0, 10), ot1)
        ot2 = get_overlap_time(traj_1, traj_2)
        self.assertEqual((0, 10), ot2)
        ot3 = get_overlap_time(traj_0, traj_2)
        self.assertEqual((0, 10), ot3)

        d = dg.get_distance(0, 1)
        self.assertEqual(0.01225, d)

        d = dg.get_distance(1, 2)
        self.assertEqual(0.01225, d)

        d = dg.get_distance(0, 2)
        self.assertEqual(0.02449, d)

        # Add another trajectory
        new_t = Trajectory("C")
        new_t.add_location(TimestampedLocation(0, 15, 15))
        new_t.add_location(TimestampedLocation(5, 20, 20))
        new_t.add_location(TimestampedLocation(10, 25, 25))
        dg.add_node(new_t)

        # Distances between already present trajectories shouldn't change
        d = dg.get_distance(0, 1)
        self.assertEqual(0.01225, d)
        d = dg.get_distance(1, 2)
        self.assertEqual(0.01225, d)
        d = dg.get_distance(0, 2)
        self.assertEqual(0.02449, d)

        d = dg.get_distance(0, "C")
        self.assertEqual(0.03674, d)

        dg.draw_graph()

    def test_4(self):
        # This dataset has 3 synchronized trajectories with different beginning and ending timestamps
        dataset = get_mock_dataset_4()

        dg = DistanceGraph(dataset)
        dg.compute()

        traj_0 = dataset.get_trajectory(0)
        traj_1 = dataset.get_trajectory(1)
        traj_2 = dataset.get_trajectory(2)

        p1 = get_p_contemporary(traj_0, traj_1)
        self.assertEqual(50.00, p1)
        p2 = get_p_contemporary(traj_1, traj_2)
        self.assertEqual(50.00, p2)
        p3 = get_p_contemporary(traj_0, traj_2)
        self.assertEqual(0.00, p3)

        ot1 = get_overlap_time(traj_0, traj_1)
        self.assertEqual((5, 10), ot1)
        ot2 = get_overlap_time(traj_1, traj_2)
        self.assertEqual((10, 15), ot2)
        ot3 = get_overlap_time(traj_0, traj_2)
        self.assertEqual((10, 10), ot3)

        d = dg.get_distance(0, 1)
        self.assertEqual(0.0, d)

        d = dg.get_distance(1, 2)
        self.assertEqual(0.0, d)

        d = dg.get_distance(0, 2)
        self.assertEqual(None, d)

        # Add another trajectory
        new_t = Trajectory("C")
        new_t.add_location(TimestampedLocation(15, 15, 15))
        new_t.add_location(TimestampedLocation(20, 20, 20))
        new_t.add_location(TimestampedLocation(25, 25, 25))
        dg.add_node(new_t)

        # Distances between already present trajectories shouldn't change
        d = dg.get_distance(0, 1)
        self.assertEqual(0.0, d)
        d = dg.get_distance(1, 2)
        self.assertEqual(0.0, d)
        d = dg.get_distance(0, 2)
        self.assertEqual(None, d)

        # Not overlapped
        d = dg.get_distance(0, "C")
        self.assertEqual(None, d)

        d = dg.get_distance(1, "C")
        self.assertEqual(None, d)

        d = dg.get_distance(2, "C")
        self.assertEqual(0.0, d)

        dg.draw_graph()

    def test_5(self):
        # This dataset has 3 unsynchronized trajectories with same beginning and ending timestamps
        dataset = get_mock_dataset_5()

        dg = DistanceGraph(dataset)
        dg.compute()

        traj_0 = dataset.get_trajectory(0)
        traj_1 = dataset.get_trajectory(1)
        traj_2 = dataset.get_trajectory(2)

        p1 = get_p_contemporary(traj_0, traj_1)
        self.assertEqual(100.00, p1)
        p2 = get_p_contemporary(traj_1, traj_2)
        self.assertEqual(100.00, p2)
        p3 = get_p_contemporary(traj_0, traj_2)
        self.assertEqual(100.00, p3)

        ot1 = get_overlap_time(traj_0, traj_1)
        self.assertEqual((0, 25), ot1)
        ot2 = get_overlap_time(traj_1, traj_2)
        self.assertEqual((0, 25), ot2)
        ot3 = get_overlap_time(traj_0, traj_2)
        self.assertEqual((0, 25), ot3)

        print(dg.synchronyzed_trajectories[0])
        print(dg.synchronyzed_trajectories[1])
        print(dg.synchronyzed_trajectories[2])

        d = dg.get_distance(0, 1)
        self.assertEqual(0.00535, d)
        d = dg.get_distance(1, 2)
        self.assertEqual(0.00530, d)
        d = dg.get_distance(0, 2)
        self.assertEqual(0.01060, d)

        # Add another trajectory
        new_t = Trajectory("C")
        new_t.add_location(TimestampedLocation(0, 15, 15))
        new_t.add_location(TimestampedLocation(5, 20, 20))
        new_t.add_location(TimestampedLocation(25, 25, 25))
        dg.add_node(new_t)

        print(dg.synchronyzed_trajectories[0])
        print(dg.synchronyzed_trajectories[1])
        print(dg.synchronyzed_trajectories[2])
        print(dg.synchronyzed_trajectories[3])

        # dg.draw_graph()

    def test_6(self):

        dataset = get_mock_dataset_N(9)
        distance = Distance(dataset)
        d = distance.compute(0, 3)
        self.assertEqual(0.01485, d)
        d = distance.compute(0, 7)
        self.assertEqual(0.08245, d)
        d = distance.compute(0, 5)
        self.assertEqual(0.13634, d)
        d = distance.compute(5, 6)
        self.assertEqual(0.03349, d)
        d = distance.compute(0, 6)
        self.assertEqual(0.18781, d)

        # dg.draw_graph()

    def test_7(self):

        dataset = get_mock_dataset_7()
        distance = Distance(dataset)

        distance.distance_graph.draw_graph()

        distance.filter_dataset()
        distance.distance_graph.draw_graph()


    def test_10(self):
        # This dataset has 3 unsynchronized trajectories with same beginning and ending timestamps
        dataset = get_mock_dataset_5()

        distance = Distance(dataset)
        t1 = Trajectory(1)
        t2 = Trajectory(4)
        d=distance.compute(t1,t2)
        print(d)

if __name__ == '__main__':
    unittest.main()
