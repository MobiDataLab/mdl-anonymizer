import logging
from collections import defaultdict

import numpy as np

from networkx import NetworkXNoPath

from src.distances.trajectory.DomingoTrujillo2012.DistanceGraph import DistanceGraph
from src.entities.Dataset import Dataset
from src.entities.Trajectory import Trajectory
from src.distances.trajectory.DistanceInterface import DistanceInterface


class Distance(DistanceInterface):

    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.distance_graph = DistanceGraph(dataset)
        self.distance_graph.compute()
        # self.distance_matrix = self.__compute_distance_matrix()
        self.distance_matrix = defaultdict(dict)

    def __compute_distance_matrix(self):
        logging.info("Computing distance matrix")

        # max_traj_id = max([t.id for t in self.dataset.trajectories])
        # matrix = np.zeros((max_traj_id+1, max_traj_id+1))
        matrix = defaultdict(dict)

        for t_1_id in self.distance_graph.get_nodes():
            if isinstance(t_1_id, np.int64):
                t_1_id = t_1_id.item()
            logging.info(f"\tComputing {t_1_id}")
            for t_2_id in self.distance_graph.get_nodes():
                if isinstance(t_2_id, np.int64):
                    t_2_id = t_2_id.item()

                try:
                    # Have we already computed the distance?
                    d = matrix[t_2_id][t_1_id]
                except KeyError:
                    try:
                        d = self.distance_graph.get_graph_distance(t_1_id, t_2_id)
                    except NetworkXNoPath:
                        # If there is no path, there is no distance
                        d = None

                matrix[t_1_id][t_2_id] = d
        logging.info("Distance matrix computed!")

        return matrix

    def __add_node_to_distance_matrix(self, new_node_id):
        logging.info("Adding node to distance matrix!")
        for t_id in self.distance_graph.graph.nodes:
            if isinstance(t_id, np.int64):
                t_id = t_id.item()
                try:
                    d = self.distance_graph.get_graph_distance(t_id, new_node_id)
                except NetworkXNoPath:
                    # If there is no path, there is no distance
                    d = None

            self.distance_matrix[t_id][new_node_id] = d
            self.distance_matrix[new_node_id][t_id] = d
        logging.info("Done!")

    def compute(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:
        # 1st try: No distance matrix. We always check distance graph to get the distance
        # try:
        #     d = self.distance_graph.get_graph_distance(trajectory1, trajectory2)
        # except NetworkXNoPath:
        #     # If there is no path, there is no distance
        #     return None

        # 2on try: Previously compute a distance matrix and get the distance from there
        # try:
        #     d = self.distance_matrix[trajectory1.id][trajectory2.id]
        # except KeyError:
        #     # Check if this trajectories exists in the distance graph
        #     if not self.distance_graph.is_included(trajectory1.id):
        #         self.distance_graph.add_node(trajectory1)
        #         # Add trajectory to the new node to the others to the distance matrix
        #         self.__add_node_to_distance_matrix(trajectory1.id)
        #     else:
        #         self.distance_graph.add_node(trajectory2)
        #         # Add trajectory to the new node to the others to the distance matrix
        #         self.__add_node_to_distance_matrix(trajectory2.id)
        #
        #     d = self.distance_matrix[trajectory1.id, trajectory2.id]

        # 3rd try: The distance matrix is initially empty. We store there every distance computed to be reused later
        try:
            d = self.distance_matrix[trajectory1.id][trajectory2.id]
        except KeyError:
            # Distance not computed
            # Exists both nodes in the distance graph?
            if trajectory1.id in self.distance_graph.get_nodes() and trajectory2.id in self.distance_graph.get_nodes():
                # Both nodes exists so it's a matter to get the distance from the graph
                d = self.distance_graph.get_graph_distance(trajectory1, trajectory2)
            else:
                # One of the two nodes does not exists in the graph. We have to add it
                if not self.distance_graph.is_included(trajectory1.id):
                    self.distance_graph.add_node(trajectory1)
                else:
                    self.distance_graph.add_node(trajectory2)

                d = self.distance_graph.get_graph_distance(trajectory1, trajectory2)

        # Store the distance for later use
        self.distance_matrix[trajectory1.id][trajectory2.id] = d
        self.distance_matrix[trajectory2.id][trajectory1.id] = d

        return d

    '''
    Return a new dataset with the trajectories of the main connected component of the distance graph
    '''
    def filter_dataset(self):
        large_component = self.distance_graph.get_large_component()
        filtered_dataset = self.dataset.__class__()
        filtered_dataset.set_description("FILTERED DATASET")
        filtered_dataset.trajectories = [t for t in self.dataset.trajectories if t.id in large_component]

        return filtered_dataset
