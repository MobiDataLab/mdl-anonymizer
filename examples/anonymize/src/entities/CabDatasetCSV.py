import csv

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.entities.Trajectory import Trajectory
from examples.anonymize.src.entities.CabLocation import CabLocation


class CabDatasetCSV(Dataset):

    def load(self, filepath, delimiter=';', quotechar='"'):

        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
            id = ""
            traj = None
            for row in reader:
                if id != row[0]:
                    # New cab
                    if traj is not None:
                        self.add_trajectory(traj)
                    id = row[0]
                    traj = Trajectory(row[0])

                loc = CabLocation(row[4], row[1], row[2], row[3])
                traj.add_location(loc)

            # Add the last trajectory
            self.add_trajectory(traj)