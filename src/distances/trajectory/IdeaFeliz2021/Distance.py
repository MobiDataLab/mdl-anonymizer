import logging
from collections import defaultdict
from math import sqrt

import numpy as np

from networkx import NetworkXNoPath

from src.distances.trajectory.DomingoTrujillo2012.DistanceGraph import DistanceGraph
from src.distances.trajectory.IdeaFeliz2021.TrajectoryUtils import get_p_contemporary, get_overlap_time
from src.entities.Dataset import Dataset
from src.entities.TimestampedLocation import TimestampedLocation
from src.entities.Trajectory import Trajectory
from src.distances.trajectory.DistanceInterface import DistanceInterface
from src.utils.Interpolation import interpolate


class Distance(DistanceInterface):

    def __init__(self, dataset: Dataset):
        '''
        Ni grafo ni ostias. Trayectorias que no son contemporanias tienen distancia infinita.
        :param dataset:
        '''
        self.dataset = dataset
        self.distance_matrix = defaultdict(dict)


    def compute(self, trajectory1: Trajectory, trajectory2: Trajectory) -> float:

        try:
            d = self.distance_matrix[trajectory1.id][trajectory2.id]
        except KeyError:
            # Distance not computed
            p = get_p_contemporary(trajectory1, trajectory2)
            if p > 0:

                # avg_speed_1 = trajectory1.get_avg_speed(sp_type=self.spatial_distance)
                # avg_speed_2 = trajectory2.get_avg_speed(sp_type=self.spatial_distance)
                # avg_speed = (avg_speed_1 + avg_speed_2) / 2
                d = 0.0
                s_traj_1, s_traj_2 = self.synchronize(trajectory1, trajectory2)

                ot = get_overlap_time(s_traj_1, s_traj_2)
                ts_interval = s_traj_1.get_interval_timestamps(ot)

                for ts in ts_interval:
                    loc1 = s_traj_1.get_location_by_timestamp(ts)
                    loc2 = s_traj_2.get_location_by_timestamp(ts)

                    d += loc1.spatial_distance(loc2)

                d /= pow(max(ot) - min(ot), 2)
                d = sqrt(d)
                d /= p

                # sub_1 = s_traj_1.filter_by_interval(ot)
                # sub_2 = s_traj_2.filter_by_interval(ot)
                #
                # h = round((len(sub_1) + len(sub_2)) / 2)
                # gap_1 = len(sub_1) / h
                # gap_2 = len(sub_2) / h
                #
                # index_1 = index_2 = 0
                # i = j = 0
                #
                # d = 0
                #
                # for k in range(h):
                #
                #     if i >= len(sub_1):
                #         i = len(sub_1) - 1
                #
                #     if j >= len(sub_2):
                #         j = len(sub_2) - 1
                #
                #     loc_1 = sub_1[i]
                #     loc_2 = sub_2[j]
                #
                #     d += (loc_1.spatial_distance(loc_2, type=self.spatial_distance) +
                #           self.landa * (loc_1.temporal_distance(loc_2)) * avg_speed)
                #
                #     index_1 += gap_1
                #     index_2 += gap_2
                #
                #     i = round(index_1)
                #     j = round(index_2)
                #
                # d /= h

                # d = sqrt(d)

            else:
                d = 9999999999999

        # Store the distance for later use
        self.distance_matrix[trajectory1.id][trajectory2.id] = d
        self.distance_matrix[trajectory2.id][trajectory1.id] = d

        return d

    def synchronize(self, trajectory1, trajectory2):

        timestamps1 = trajectory1.get_timestamps()
        timestamps2 = trajectory2.get_timestamps()
        timestamps = list(set(timestamps1 + timestamps2))

        synchro_1 = self.__synchronize_trajectory(trajectory1, timestamps)
        synchro_2 = self.__synchronize_trajectory(trajectory2, timestamps)

        return synchro_1, synchro_2


    def __synchronize_trajectory(self, T: Trajectory, timestamps):
        synchro_T = Trajectory(T.id)
        filter_timestamps = [t for t in timestamps if (T.get_first_timestamp() <= t <= T.get_last_timestamp())]
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

    def filter_dataset(self):
        return self.dataset
