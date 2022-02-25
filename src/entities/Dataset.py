import csv
import datetime
import logging

import pandas

from abc import ABC

from src.entities.Trajectory import Trajectory
from examples.anonymize.src.entities.CabLocation import CabLocation


class Dataset(ABC):
    def __init__(self):
        self.trajectories = []
        self.description = None

#    @abstractmethod
#    def load(self):
#        raise NotImplementedError

    def load_from_scikit(self, filename, n_trajectories = None, min_locations = 10,
                         latitude_key="lat", longitude_key="lon", datetime_key="datetime", user_key = "user_id",
                         datetime_format = "%Y/%m/%d %H:%M:%S"):
        df = pandas.read_csv(filename)

        user_id = df.loc[0, user_key]

        T = Trajectory(user_id)
        for index, row in df.iterrows():
            if user_id == row[user_key]:

                # Convert datetime to timestamp
                element = datetime.datetime.strptime(row[datetime_key], datetime_format)
                timestamp = datetime.datetime.timestamp(element)

                location = CabLocation(timestamp,  row[latitude_key],  row[longitude_key])
                T.add_location(location)
            else:
                if len(T.locations) >= min_locations:
                    T.locations.sort(key=lambda x: x.timestamp)
                    self.add_trajectory(T)

                    if n_trajectories and len(self.trajectories) >= n_trajectories:
                        break

                user_id = row[user_key]
                T = Trajectory(user_id)

                # Convert datetime to timestamp
                element = datetime.datetime.strptime(row[datetime_key], datetime_format)
                timestamp = datetime.datetime.timestamp(element)
                location = CabLocation(timestamp, row[latitude_key], row[longitude_key])
                T.add_location(location)
        else:
            if len(T.locations) >= min_locations:
                T.locations.sort(key=lambda x: x.timestamp)
                self.add_trajectory(T)

        logging.info(f"Dataset loaded: {len(self)} trajectories. Every trajectory has, at least, {min_locations} locations")

    '''
        Export a loaded dataset as scikit dataset
    '''

    def export_to_scikit(self, filename="scikit_dataset.csv"):
        if not self.is_loaded():
            raise RuntimeError("Dataset is not loaded")

        with open(filename, mode='w', newline='') as new_file:
            writer = csv.writer(new_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["lat", "lon", "datetime", "user_id"])
            for t in self.trajectories:
                for l in t.locations:
                    date_time = datetime.datetime.fromtimestamp(l.timestamp)
                    writer.writerow([l.x, l.y, date_time.strftime("%Y/%m/%d %H:%M:%S"), t.id])

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
        logging.info(f"Dataset filtered. Removed trajectories with less than {min_locations} locations. Now it has {len(self)} trajectories.")

    def __len__(self):
        return len(self.trajectories)

    def __repr__(self):
        ret = ""
        if self.description:
            ret += f"{self.description}\n"
        for T in self.trajectories:
            ret += f'{str(T)}\n'

        return ret
