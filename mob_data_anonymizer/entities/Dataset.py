import csv
import datetime
import logging
from functools import reduce

import pandas
import numpy as np
import pyarrow.parquet as pq

from abc import ABC

from skmob import TrajDataFrame
from tqdm import tqdm

from mob_data_anonymizer.entities.Trajectory import Trajectory
from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation


class Dataset(ABC):
    def __init__(self):
        self.trajectories = []
        self.description = None

    #    @abstractmethod
    #    def load(self):
    #        raise NotImplementedError

    def from_file(self, filename, n_trajectories=None, min_locations=0,
                  latitude_key="lat", longitude_key="lon", datetime_key="datetime", user_key="user_id",
                  trajectory_key="trajectory_id",
                  datetime_format="%Y/%m/%d %H:%M:%S"):

        """
        Import a dataset from a CSV or parquet file
        """

        logging.info("Loading dataset...")

        if filename[-4:] == '.csv':
            df = pandas.read_csv(filename)
        elif filename[-8:] == '.parquet':
            # df = pandas.read_parquet(filename)
            df = pq.read_table(filename).to_pandas()
        else:
            raise Exception("File format not supported")

        # Get the first trajectory and user id
        traj_id = df.loc[0, trajectory_key]
        user_id = df.loc[0, user_key]

        users_count = 1

        pbar = tqdm(total=len(df))

        T = Trajectory(traj_id, user_id)
        for index, row in df.iterrows():
            if traj_id == row[trajectory_key]:

                # Convert datetime to timestamp
                element = datetime.datetime.strptime(row[datetime_key], datetime_format)
                timestamp = datetime.datetime.timestamp(element)

                location = TimestampedLocation(timestamp, row[latitude_key], row[longitude_key])
                T.add_location(location)
            else:
                if len(T.locations) >= min_locations:
                    T.locations.sort(key=lambda x: x.timestamp)
                    self.add_trajectory(T)

                    if n_trajectories and len(self.trajectories) >= n_trajectories:
                        break

                traj_id = row[trajectory_key]

                if row[user_key] != user_id:
                    users_count += 1
                    user_id = row[user_key]

                T = Trajectory(traj_id, user_id)

                # Convert datetime to timestamp
                element = datetime.datetime.strptime(row[datetime_key], datetime_format)
                timestamp = datetime.datetime.timestamp(element)
                location = TimestampedLocation(timestamp, row[latitude_key], row[longitude_key])
                T.add_location(location)

            pbar.update(1)
        else:
            if len(T.locations) >= min_locations:
                T.locations.sort(key=lambda x: x.timestamp)
                self.add_trajectory(T)

        count_locations = sum([len(t) for t in self.trajectories])

        logging.info(
            f"Dataset loaded: {len(self)} trajectories, {count_locations} locations, from {users_count} users. "
            f"Every trajectory has, at least, {min_locations} locations")

    def to_csv(self, filename="output_dataset.csv"):
        """
        Export a loaded dataset to a csv
        """
        if not self.is_loaded():
            raise RuntimeError("Dataset is not loaded")

        logging.info("Writing dataset...")

        with open(filename, mode='w', newline='') as new_file:
            writer = csv.writer(new_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["lat", "lon", "datetime", "trajectory_id", "user_id"])
            for t in self.trajectories:
                for l in t.locations:
                    date_time = datetime.datetime.fromtimestamp(l.timestamp)
                    writer.writerow([l.x, l.y, date_time.strftime("%Y/%m/%d %H:%M:%S"), t.id, t.user_id])

    def from_tdf(self, tdf: TrajDataFrame):

        # Sort by uid
        tdf.sort_values('uid')

        user_id = tdf.loc[0, 'uid']

        T = Trajectory(user_id)

        for index, row in tdf.iterrows():
            # Change of trajectory
            if user_id != row['uid']:
                T.locations.sort(key=lambda x: x.timestamp)
                self.add_trajectory(T)

                user_id = row['uid']
                T = Trajectory(user_id)

            # Add new location
            timestamp = row['datetime'].timestamp()
            location = TimestampedLocation(timestamp, row['lat'], row['lng'])
            T.add_location(location)

        # Add the last trajectory
        T.locations.sort(key=lambda x: x.timestamp)
        self.add_trajectory(T)

    def to_tdf(self):

        df = pandas.DataFrame()

        for traj in self.trajectories:
            for loc in traj.locations:
                df2 = pandas.DataFrame(
                    {'lat': [loc.x],
                     'lng': [loc.y],
                     'datetime': [loc.timestamp],
                     'uid': [traj.id],
                     })
                df = pandas.concat([df, df2], ignore_index=True)

        return TrajDataFrame(df, timestamp=True)

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

    def __len__(self):
        return len(self.trajectories)

    def __repr__(self):
        ret = ""
        if self.description:
            ret += f"{self.description}\n"
        for T in self.trajectories:
            ret += f'{str(T)}\n'

        return ret
