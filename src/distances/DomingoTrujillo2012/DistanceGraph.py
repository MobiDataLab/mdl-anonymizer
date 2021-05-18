import logging
import math
import networkx as nx
import matplotlib.pyplot as plt

from src.distances.DomingoTrujillo2012.TrajectoryUtils import get_p_contemporary, get_overlap_time
from src.entities.Dataset import Dataset
from src.entities.TimestampedLocation import TimestampedLocation
from src.entities.Trajectory import Trajectory
from src.utils.Interpolation import interpolate


class DistanceGraph:
    def __init__(self, dataset: Dataset = None):
        if dataset and dataset.is_loaded():
            self.dataset = dataset

        self.graph = nx.Graph()

    def compute(self):
        logging.info("Computing distance graph")
        try:
            dataset = self.dataset
        except AttributeError as err:
            raise Exception("Dataset not loaded") from None

        self.__synchronize_trajectories()
        logging.debug(self.synchronyzed_trajectories)
        logging.info("\tTrajectories synchronized")

        self.__build_graph()

        logging.info("Distance graph computed!")

    def __synchronize_trajectories(self):
        # Collect all timestamps
        timestamps = []
        for T in self.dataset.trajectories:
            for L in T.locations:
                timestamps.append(L.timestamp)

        # Converting to set we remove duplicates
        timestamps = list(set(timestamps))
        timestamps.sort()

        self.synchronyzed_trajectories = []
        for T_i in self.dataset.trajectories:
            synchro_T = self.__synchronize_trajectory(T_i, timestamps)
            self.synchronyzed_trajectories.append(synchro_T)
            # logging.debug(f'Trajectory {T_i.id} synchronized!')

        # logging.debug(self.synchronyzed_trajectories)

    def __get_synchro_trajectory(self, id):
        for t in self.synchronyzed_trajectories:
            if t.id == id:
                return t
        return None

    def __synchronize_trajectory(self, T: Trajectory, timestamps):

        synchro_T = Trajectory(T.id)
        filter_timestamps = [t for t in timestamps if (T.first_timestamp() <= t <= T.last_timestamp())]
        for ts in filter_timestamps:
            loc = T.get_location_by_timestamp(ts)
            if loc:
                synchro_T.add_location(loc)
            else:
                # Interpolate
                prev_loc = T.get_previous_location_by_timestamp(ts)
                next_loc = T.get_next_location_by_timestamp(ts)
                point = interpolate(prev_loc, next_loc, ts)
                interpolated_location = TimestampedLocation(ts, round(point[0], 6), round(point[1], 6))
                synchro_T.add_location(interpolated_location)

        return synchro_T

    def __resynchronize_trajectories(self, new_t: Trajectory):
        if not self.synchronyzed_trajectories:
            raise Exception("Dataset trajectories must already be synchronized")

        # Collect previous timestamps
        timestamps = []
        for T in self.synchronyzed_trajectories:
            for L in T.locations:
                timestamps.append(L.timestamp)

        # And the new ones
        for L in new_t.locations:
            timestamps.append(L.timestamp)

        # Converting to set we remove duplicates
        timestamps = list(set(timestamps))
        timestamps.sort()

        # TODO: Estamos resynchronizando todos los timestamps de todas las trayectorías.
        #       En realidad, solo haría falta calcular los nuevos timestamps
        self.synchronyzed_trajectories = []
        for T_i in self.dataset.trajectories:
            synchro_T = self.__synchronize_trajectory(T_i, timestamps)
            self.synchronyzed_trajectories.append(synchro_T)
            # logging.debug(f'Trajectory {T_i.id} resynchronized!')

        # Finally add the synchronized new trajectory
        synchro_T = self.__synchronize_trajectory(new_t, timestamps)
        self.synchronyzed_trajectories.append(synchro_T)

        logging.info("\tTrajectories re-synchronized")

    def get_distance(self, s_traj_1, s_traj_2):

        if not isinstance(s_traj_1, Trajectory):
            id = s_traj_1
            s_traj_1 = self.__get_synchro_trajectory(s_traj_1)
            if s_traj_1 is None:
                raise Exception(f"Trajectory {id} doesn't exist")
        if not isinstance(s_traj_2, Trajectory):
            id = s_traj_2
            s_traj_2 = self.__get_synchro_trajectory(s_traj_2)
            if s_traj_2 is None:
                raise Exception(f"Trajectory {id} doesn't exist")

        p = get_p_contemporary(s_traj_1, s_traj_2)
        # logging.debug(f'\tp-contemporary: {p}')
        if p > 0:
            # p-contemporanies
            ot = get_overlap_time(s_traj_1, s_traj_2)
            # logging.debug(f'\tot: {ot}')
            ts_interval = s_traj_1.get_interval_timestamps(ot)
            # logging.debug(f'\tts_interval length: {len(ts_interval)}')

            d = 0
            denominator = pow(max(ot) - min(ot), 2)
            for ts in ts_interval:
                loc_1 = s_traj_1.get_location_by_timestamp(ts)
                loc_2 = s_traj_2.get_location_by_timestamp(ts)
                d += (pow(loc_1.x - loc_2.x, 2) + pow(loc_1.y - loc_2.y, 2)) / denominator

            d = math.sqrt(d)
            d = d / p

            return d
        else:
            return None

    def __build_graph(self):

        # Add nodes
        self.graph.add_nodes_from([t.id for t in self.synchronyzed_trajectories])

        for T_i in self.synchronyzed_trajectories:
            for T_j in self.synchronyzed_trajectories:
                # logging.debug(f'Computing distance ({T_i.id, T_j.id})')
                if T_i != T_j:
                    # Check if an edge between T_i and T_l already exists
                    if T_j.id not in self.graph.nodes() or T_i.id not in list(self.graph.neighbors(T_j.id)):
                        # logging.debug(f'\tActually computing ({T_i.id, T_j.id})')
                        d = self.get_distance(T_i, T_j)
                        # logging.debug(f'\td =  {d}')
                        if d is not None:
                            self.graph.add_edge(T_i.id, T_j.id, weight=d)

    def draw_graph(self):
        pos = nx.spring_layout(self.graph)
        plt.figure()
        nx.draw(self.graph, pos, with_labels=True, font_weight='bold', node_color="white", edgecolors="black")
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_color='red')

        plt.show()

    def get_graph_distance(self, s_traj_1, s_traj_2):

        if isinstance(s_traj_1, int) or isinstance(s_traj_1, str):
            s_traj_1 = self.__get_synchro_trajectory(s_traj_1)
        if isinstance(s_traj_2, int) or isinstance(s_traj_2, str):
            s_traj_2 = self.__get_synchro_trajectory(s_traj_2)

        # Modification regarding the distance of the paper:
        # If a direct distance exists -> return distance
        # Else: compute shortest path

        if self.graph.get_edge_data(s_traj_1.id, s_traj_2.id):
            return self.graph[s_traj_1.id][s_traj_2.id]["weight"]

        return nx.shortest_path_length(self.graph, s_traj_1.id, s_traj_2.id, "weight")

    def get_components(self):
        return nx.connected_components(self.graph)

    def get_large_component(self):
        return max(nx.connected_components(self.graph), key=len)

    def is_included(self, t_id):
        return t_id in self.graph

    def add_node(self, t: Trajectory):

        logging.info(f"Adding new node: {t.id}")
        # Synchronize
        self.__resynchronize_trajectories(t)

        self.graph.add_node(t.id)

        for T_i in self.synchronyzed_trajectories:
            d = self.get_distance(t, T_i)
            if d is not None:
                self.graph.add_edge(t.id, T_i.id, weight=d)

        logging.info(f"New node added: {t.id}")

    def get_nodes(self):
        return self.graph.nodes
