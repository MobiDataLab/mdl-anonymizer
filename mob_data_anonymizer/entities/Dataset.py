import csv
import datetime
import logging
from functools import reduce
import random
import pandas
import numpy as np
import pyarrow.parquet as pq

from abc import ABC

import pytz
from geopandas import GeoDataFrame
from shapely import geometry
from skmob import TrajDataFrame
from skmob.utils import constants
from skmob.utils.constants import DEFAULT_CRS
from tqdm import tqdm

from mob_data_anonymizer.entities.Trajectory import Trajectory
from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation

class Dataset(ABC):
    def __init__(self):
        self.trajectories = []
        self.description = None
        self.sample = None

        self.timezone = pytz.timezone("UTC")

    #    @abstractmethod
    #    def load(self):
    #        raise NotImplementedError

    def from_file(self, filename, n_trajectories=None, min_locations=0,
                  latitude_key="lat", longitude_key="lon", datetime_key="datetime", user_key="user_id",
                  trajectory_key="trajectory_id",
                  datetime_format="%Y/%m/%d %H:%M:%S",
                  sample=None):

        """
        Load a dataset from a CSV or parquet file

        Note: datetimes are always considered in UTC timezone
        """

        logging.info("Loading dataset...")
        self.sample = sample

        if filename[-4:] == '.csv':
            df = pandas.read_csv(filename)
        elif filename[-8:] == '.parquet':
            # df = pandas.read_parquet(filename)
            df = pq.read_table(filename).to_pandas()
        else:
            raise Exception("File format not supported")

        # Order by traj_id
        df.sort_values(trajectory_key, inplace=True)

        # Get the first trajectory and user id
        traj_id = df.loc[0, trajectory_key]
        user_id = df.loc[0, user_key]

        users = set([])

        pbar = tqdm(total=len(df))

        T = Trajectory(traj_id, user_id)
        for index, row in df.iterrows():
            if traj_id == row[trajectory_key]:

                # Convert datetime to timestamp
                element = datetime.datetime.strptime(row[datetime_key], datetime_format)
                element = self.timezone.localize(element)
                timestamp = datetime.datetime.timestamp(element)

                location = TimestampedLocation(timestamp, row[longitude_key], row[latitude_key])
                T.add_location(location)
            else:
                if len(T.locations) >= min_locations:
                    T.locations.sort(key=lambda x: x.timestamp)
                    self.add_trajectory(T)

                    if n_trajectories and len(self.trajectories) >= n_trajectories:
                        break

                traj_id = row[trajectory_key]
                user_id = row[user_key]
                users.add(user_id)

                T = Trajectory(traj_id, user_id)

                # Convert datetime to timestamp
                element = datetime.datetime.strptime(row[datetime_key], datetime_format)
                element = self.timezone.localize(element)
                timestamp = datetime.datetime.timestamp(element)
                location = TimestampedLocation(timestamp, row[longitude_key], row[latitude_key])
                T.add_location(location)

            pbar.update(1)
        else:
            if len(T.locations) >= min_locations:
                T.locations.sort(key=lambda x: x.timestamp)
                self.add_trajectory(T)

        count_locations = sum([len(t) for t in self.trajectories])

        logging.info(
            f"Dataset loaded: {len(self)} trajectories, {count_locations} locations, from {len(users)} users. "
            f"Every trajectory has, at least, {min_locations} locations")

    def to_csv(self, filename="output_dataset.csv"):
        """
        Export a loaded dataset to a csv

        Note: Datetimes are written in UTC timezone
        """
        if not self.is_loaded():
            raise RuntimeError("Dataset is not loaded")

        logging.info("Writing dataset...")

        with open(filename, mode='w', newline='') as new_file:
            writer = csv.writer(new_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["lon", "lat", "datetime", "trajectory_id", "user_id"])
            for t in self.trajectories:
                for l in t.locations:
                    date_time = datetime.datetime.fromtimestamp(l.timestamp, self.timezone)
                    writer.writerow([l.x, l.y, date_time.strftime("%Y/%m/%d %H:%M:%S"), t.id, t.user_id])

    def from_tdf(self, tdf: TrajDataFrame):

        # Sort by uid
        tdf.sort_values(constants.TID)

        user_id = tdf.loc[0, constants.UID]
        traj_id = tdf.loc[0, constants.TID]

        T = Trajectory(traj_id, user_id)

        for index, row in tdf.iterrows():
            # Change of trajectory
            if traj_id != row[constants.TID]:
                T.locations.sort(key=lambda x: x.timestamp)
                self.add_trajectory(T)

                traj_id = row[constants.TID]
                user_id = row[constants.UID]
                T = Trajectory(traj_id, user_id)

            # Add new location
            timestamp = row[constants.DATETIME].timestamp()
            location = TimestampedLocation(timestamp, row[constants.LONGITUDE], row[ constants.LATITUDE])
            T.add_location(location)

        # Add the last trajectory
        T.locations.sort(key=lambda x: x.timestamp)
        self.add_trajectory(T)

    def to_tdf(self):

        df = pandas.DataFrame()

        for traj in self.trajectories:
            for loc in traj.locations:
                df2 = pandas.DataFrame(
                    {constants.LONGITUDE: [loc.x],
                     constants.LATITUDE: [loc.y],
                     constants.DATETIME: [loc.timestamp],
                     constants.UID: [traj.user_id],
                     constants.TID: [traj.id]
                     })
                df = pandas.concat([df, df2], ignore_index=True)

        tdf = TrajDataFrame(df, timestamp=True)

        return tdf

    def to_numpy(self, sort_by_timestamp=False):
        """Transforms the dataset to a NumPy array for faster processing.
        Columns correspond to lat, long, timestamp, trajectory_id and user_id.
        If desired, it can be sorted by timestamp using the sort_by_timestamp parameter.
        CAUTION: Additional parameters of the location object will not be stored!
        """
        # Get number of locations and allocate matrix
        num_locations = self.get_number_of_locations()
        np_dataset = np.empty((num_locations, 5))

        # Assign values to matrix
        idx = 0
        for traj in self.trajectories:
            for loc in traj.locations:
                np_dataset[idx][0] = loc.x
                np_dataset[idx][1] = loc.y
                np_dataset[idx][2] = loc.timestamp
                np_dataset[idx][3] = traj.id
                np_dataset[idx][4] = traj.user_id
                idx += 1

        # Sort by timestamp if required
        if sort_by_timestamp:
            np_dataset = np_dataset[np_dataset[:, 2].argsort()]

        return np_dataset

    def from_numpy(self, np_dataset: np.array):
        """Loads the dataset from a NumPy array like the generated by
        the self.to_numpy method.
        CAUTION 1: It removes all the current trajectories from the dataset.
        CAUTION 2: Additional parameters of the location object will not be loaded."""
        self.trajectories = []

        # Sort dataset by trajectory_id
        np_dataset = np_dataset[np_dataset[:, 3].argsort()]

        # Get and store trajectories
        current_traj = None
        for record in np_dataset:
            if current_traj is None:  # First trajectory
                current_traj = Trajectory(id=record[3], user_id=record[4])
            elif record[3] != current_traj.id:  # Trajectory ID changed
                self.add_trajectory(current_traj)  # Store trajectory
                current_traj = Trajectory(id=record[3], user_id=record[4])  # New trajectory
            # Add location
            loc = TimestampedLocation(record[2], record[0], record[1])
            current_traj.add_location(loc)

        # Add last trajectory
        if current_traj is not None:
            self.add_trajectory(current_traj)

    def is_loaded(self):
        return len(self.trajectories) > 0

    def set_description(self, description):
        self.description = description

    def add_trajectory(self, trajectory: Trajectory):
        self.trajectories.append(trajectory)

    def get_trajectory(self, id):
        for t in self.trajectories:
            if t.id == id:
                return t
        return None

    def get_number_of_locations(self):
        return sum([len(t) for t in self.trajectories])

    def get_max_trajectory_length(self):
        return max([len(t) for t in self.trajectories])

    def get_max_timestamp(self):
        timestamp = None
        for t in self.trajectories:
            for l in t.locations:
                if timestamp is None or l.timestamp > timestamp:
                    timestamp = l.timestamp

        return timestamp

    def get_min_timestamp(self):
        timestamp = None
        for t in self.trajectories:
            for l in t.locations:
                if timestamp is None or l.timestamp < timestamp:
                    timestamp = l.timestamp

        return timestamp

    def get_bounding_box(self):
        max_lng = max_lat = min_lat = min_lng = None

        for t in self.trajectories:
            for l in t.locations:
                if max_lat is None or l.y > max_lat:
                    max_lat = l.y
                if max_lng is None or l.x > max_lng:
                    max_lng = l.x
                if min_lat is None or l.y < min_lat:
                    min_lat = l.y
                if min_lng is None or l.x < min_lng:
                    min_lng = l.x

        point_list = [[max_lng, max_lat], [max_lng, min_lat], [min_lng, min_lat], [min_lng, max_lat]]

        poly = geometry.Polygon(point_list)

        polygon = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[poly])

        return polygon

    def filter(self, min_locations=3):
        self.trajectories = [t for t in self.trajectories if len(t) >= min_locations]

        count_locations = sum([len(t) for t in self.trajectories])

        logging.info(
            f"Dataset filtered. Removed trajectories with less than {min_locations} locations. "
            f"Now it has {len(self)} trajectories and {count_locations} locations.")

    def filter_by_speed(self, max_speed_kmh=300):
        """
        :param max_velocity: km/h
        :return:
        """
        logging.info(f"Filtering dataset by max velocity")

        self.trajectories = [t for t in self.trajectories if not t.some_speed_over(max_speed_kmh)]

        count_locations = sum([len(t) for t in self.trajectories])

        logging.info(f"Dataset filtered. Removed trajectories with some one-time speed above {max_speed_kmh}. "
                     f"Now it has {len(self)} trajectories and {count_locations} locations.")
        if self.sample is not None:
            self.trajectories = random.sample(self.trajectories, self.sample)
            count_locations = sum([len(t) for t in self.trajectories])
            logging.info(
                f"Dataset sampled. "
                f"Now it has {len(self)} trajectories and {count_locations} locations.")

    def __len__(self):
        return len(self.trajectories)

    def __repr__(self):
        ret = ""
        if self.description:
            ret += f"{self.description}\n"
        for T in self.trajectories:
            ret += f'{str(T)}\n'

        return ret
