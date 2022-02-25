import datetime

from src.entities.Dataset import Dataset
from src.entities.TimestampedLocation import TimestampedLocation
from src.entities.Trajectory import Trajectory
from src.io.IoInterface import IoInterface


class Scikit(IoInterface):

    @staticmethod
    def export_dataset(dataset: Dataset) -> list:
        pass

    @staticmethod
    def export_trajectory(trajectory: Trajectory) -> list:

        def func(loc):
            list_location = Scikit.export_location(loc)
            list_location.append(trajectory.id)
            return list_location

        list_trajectory = map(func, trajectory.locations)

        return list(list_trajectory)

    @staticmethod
    def export_location(location: TimestampedLocation) -> list:
        date_time = datetime.datetime.fromtimestamp(location.timestamp)
        return [location.x, location.y, date_time.strftime("%Y/%m/%d %H:%M:%S")]
