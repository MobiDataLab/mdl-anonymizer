import csv
import datetime
import logging
import sys
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
        self.crs = DEFAULT_CRS

    def set_crs(self, crs):
        self.crs = crs

    def _ensure_values(self, lat, lon):
        if lat < -90 or lat > 90:
            return False
        if lon < -180 or lon > 180:
            return False

        return True

    #    @abstractmethod
    #    def load(self):
    #        raise NotImplementedError

    def from_file(self, filename, filetype=None, n_trajectories=None, min_locations=0,
                  latitude_key="lat", longitude_key="lon", datetime_key="timestamp", user_key="user_id",
                  trajectory_key="trajectory_id",
                  datetime_format="%Y/%m/%d %H:%M:%S",
                  sample=None):

        """
        Load a dataset from a CSV or parquet file

        Note: datetimes are always considered in UTC timezone
        """

        self.sample = sample

        if type(filename) is str:
            logging.info("Loading dataset...")
            if filename[-4:] == '.csv':
                df = pandas.read_csv(filename)
            elif filename[-8:] == '.parquet':
                # df = pandas.read_parquet(filename)
                df = pq.read_table(filename).to_pandas()
            else:
                raise TypeError("File format not supported")
        else:  # file object from api
            logging.info("Loading dataset from file object...")
            if filetype[-8:] == '.parquet':
                df = pq.read_table(filename).to_pandas()
            else:
                with open("temp.csv", 'wb') as out_file:
                    content = filename.read()  # async read
                    out_file.write(content)  # async write
                df = pandas.read_csv("temp.csv")

        # Order by traj_id
        df.sort_values(trajectory_key, inplace=True)

        # Get the first trajectory and user id
        traj_id = df.loc[0, trajectory_key]
        user_id = df.loc[0, user_key]

        users = set([])

        pbar = tqdm(total=len(df))

        wrong_values = False
        T = Trajectory(traj_id, user_id)
        for index, row in df.iterrows():
            if traj_id == row[trajectory_key]:

                # Check values
                if not self._ensure_values(row[latitude_key], row[longitude_key]):
                    wrong_values = True
                else:
                    # Add location to current trajectory

                    # Convert datetime to timestamp
                    element = datetime.datetime.strptime(row[datetime_key], datetime_format)
                    element = self.timezone.localize(element)
                    timestamp = datetime.datetime.timestamp(element)

                    location = TimestampedLocation(timestamp, row[longitude_key], row[latitude_key])
                    T.add_location(location, sort=False)
            else:
                # Sort locations and add trajectory
                if len(T.locations) >= min_locations and not wrong_values:
                    T.locations.sort(key=lambda x: x.timestamp)
                    self.add_trajectory(T)

                    if n_trajectories and len(self.trajectories) >= n_trajectories:
                        break

                # Create another trajectory
                wrong_values = False
                traj_id = row[trajectory_key]
                user_id = row[user_key]
                users.add(user_id)

                T = Trajectory(traj_id, user_id)

                if not self._ensure_values(row[latitude_key], row[longitude_key]):
                    wrong_values = True
                else:
                    # Convert datetime to timestamp
                    element = datetime.datetime.strptime(row[datetime_key], datetime_format)
                    element = self.timezone.localize(element)
                    timestamp = datetime.datetime.timestamp(element)
                    location = TimestampedLocation(timestamp, row[longitude_key], row[latitude_key])
                    T.add_location(location, sort=False)

            pbar.update(1)
        else:
            # Sort and add last trajectory
            if len(T.locations) >= min_locations:
                T.locations.sort(key=lambda x: x.timestamp)
                self.add_trajectory(T)

        count_locations = sum([len(t) for t in self.trajectories])

        logging.info(
            f"Dataset loaded: {len(self)} trajectories, {count_locations} locations, from {len(users)} users. "
            f"Every trajectory has, at least, {min_locations} locations")

        if self.sample is not None:
            self.trajectories = random.sample(self.trajectories, self.sample)
            count_locations = sum([len(t) for t in self.trajectories])
            logging.info(
                f"Dataset sampled. "
                f"Now it has {len(self)} trajectories and {count_locations} locations.")

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
            writer.writerow(["lon", "lat", "timestamp", "trajectory_id", "user_id"])
            for t in self.trajectories:
                for l in t.locations:
                    date_time = datetime.datetime.fromtimestamp(l.timestamp, self.timezone)
                    writer.writerow([l.x, l.y, date_time.strftime("%Y/%m/%d %H:%M:%S"), t.id, t.user_id])

    def from_tdf(self, tdf: TrajDataFrame):

        # Sort by uid
        tdf.sort_values(constants.TID)

        user_id = tdf[constants.UID].iloc[0]
        traj_id = tdf[constants.TID].iloc[0]

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
            location = TimestampedLocation(timestamp, row[constants.LONGITUDE], row[constants.LATITUDE])
            T.add_location(location, sort=False)

        # Add the last trajectory
        T.locations.sort(key=lambda x: x.timestamp)
        self.add_trajectory(T)

    def to_tdf(self):

        rows = [[loc.x, loc.y, loc.timestamp, traj.user_id, traj.id] for traj in self.trajectories
                for loc in traj.locations]
        df = pandas.DataFrame(rows, columns=[constants.LONGITUDE, constants.LATITUDE, constants.DATETIME,
                                             constants.UID, constants.TID])
        tdf = TrajDataFrame(df, timestamp=True)

        tdf[constants.LONGITUDE] = tdf[constants.LONGITUDE].astype(np.float32)
        tdf[constants.LATITUDE] = tdf[constants.LATITUDE].astype(np.float32)
        tdf[constants.UID] = tdf[constants.UID].astype(np.int32)
        tdf[constants.TID] = tdf[constants.TID].astype(np.int32)

        tdf.crs = self.crs

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
                current_traj = Trajectory(id=int(record[3]), user_id=int(record[4]))
            elif record[3] != current_traj.id:  # Trajectory ID changed
                self.add_trajectory(current_traj)  # Store trajectory
                current_traj = Trajectory(id=int(record[3]), user_id=int(record[4]))  # New trajectory
            # Add location
            loc = TimestampedLocation(record[2], record[0], record[1])
            current_traj.add_location(loc, sort=False)

        # Add last trajectory
        if current_traj is not None:
            self.add_trajectory(current_traj)

        self.sort_trajectories()

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

    def get_n_locations_longest_trajectory(self):
        '''
        Return the number of locations of the longest trajectory
        :return:
        '''
        if len(self.trajectories) > 0:
            return max([len(t) for t in self.trajectories])

        return None

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

    def sort_trajectories(self):
        """
        Sort the locations of all the trajectories in the dataset by timestamp
        :return:
        """
        for t in self.trajectories:
            t.locations.sort(key=lambda x: x.timestamp)

    def get_bounding_box(self) -> GeoDataFrame:
        """
        Return a GeoDataFrame with the bounding box of the dataset
        :return:
        """
        max_lng = max_lat = min_lat = min_lng = None

        for t in self.trajectories:
            for l in t.locations:
                if max_lat is None or l.y > max_lat:
                    max_lat = round(l.y, 5)
                if max_lng is None or l.x > max_lng:
                    max_lng = round(l.x, 5)
                if min_lat is None or l.y < min_lat:
                    min_lat = round(l.y, 5)
                if min_lng is None or l.x < min_lng:
                    min_lng = round(l.x, 5)

        point_list = [[max_lng, max_lat], [max_lng, min_lat], [min_lng, min_lat], [min_lng, max_lat]]

        poly = geometry.Polygon(point_list)

        polygon = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[poly])

        return polygon

    def filter_by_n_locations(self, min_locations=3):
        self.trajectories = [t for t in self.trajectories if len(t) >= min_locations]

        count_locations = sum([len(t) for t in self.trajectories])

        logging.info(
            f"Dataset filtered. Removed trajectories with less than {min_locations} locations. "
            f"Now it has {len(self)} trajectories and {count_locations} locations.")

    def filter_by_speed(self, max_speed_kmh=300):
        """
        :param max_speed_kmh: km/h
        :return:
        """
        logging.info(f"Filtering dataset by max velocity")

        self.trajectories = [t for t in self.trajectories if not t.some_speed_over(max_speed_kmh)]

        count_locations = sum([len(t) for t in self.trajectories])

        logging.info(f"Dataset filtered. Removed trajectories with some one-time speed above {max_speed_kmh}. "
                     f"Now it has {len(self)} trajectories and {count_locations} locations.")

    def filter_by_length(self, min_length: float = 0, max_length: float = sys.maxsize):
        """
        :param min_length: in km
        :param max_length: in km
        :return:
        """

        logging.info(f"Filtering dataset by trajectory length")
        self.trajectories = [t for t in self.trajectories if min_length <= t.get_length() <= max_length]
        count_locations = sum([len(t) for t in self.trajectories])
        logging.info(f"Dataset filtered."
                     f"Now it has {len(self)} trajectories and {count_locations} locations.")

    def __len__(self):
        return len(self.trajectories)

    def __repr__(self):
        ret = f"Dataset: {self.description}\n"

        if not self.trajectories:
            ret += 'EMPTY!'
        else:
            for T in self.trajectories:
                ret += f'{str(T)}\n'

        return ret
