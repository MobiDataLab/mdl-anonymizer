import logging
import csv
from datetime import datetime

from src.entities.Dataset import Dataset
from src.entities.Trajectory import Trajectory
from examples.anonymize.src.entities.CabLocation import CabLocation


class CabDatasetTXT(Dataset):

    def load_from_folder(self, folder="", n_trajectories = None, n_locations = None):

        main_file = open(f"{self.folder}/_cabs.txt", "r")
        for i, line in enumerate(main_file):
            # Read the first 'n_trajectories' lines
            if n_trajectories and i >= n_trajectories:
                break
            str = line.replace('<cab id="', '').replace('" updates="', ' ').replace('"/>', '')
            list = str.split()
            id = list[0]
            cab_file = open(f'{self.folder}/new_{id}.txt', "r")
            locations = []
            for j, cab_line in enumerate(cab_file):
                # Read the first 'n_locations' lines
                if n_locations and j >= n_locations:
                    break

                cab_list = cab_line.split()
                loc = CabLocation(cab_list[3],  cab_list[0],  cab_list[1],  cab_list[2])
                locations.append(loc)

            locations.sort(key=lambda x: x.timestamp)

            T = Trajectory(id)
            for l in locations:
                T.add_location(l)

            self.add_trajectory(T)
            cab_file.close()

        main_file.close()
        logging.info("Dataset Loaded")
        logging.info(f"Number of trajectories: {len(self.trajectories)}")
        logging.info(f"Total of locations: {self.get_number_of_locations()}")

    '''
    Build a new dataset to be used with scikit.
    Just take the trajectories of cabs occupied by a customer.
    '''
    def files_to_scikit_mobility_dataset(self, filename = 'cabs_scikit.csv', max_trajectories = 1000):
        main_file = open(f"{self.folder}/_cabs.txt", "r")
        with open(filename, mode='w') as new_file:
            writer = csv.writer(new_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["lat", "lon", "timestamp", "user_id"])
            num_trajectories = 0
            trajectory_id = 0
            recording_trajectory = False
            for i, line in enumerate(main_file):
                str = line.replace('<cab id="', '').replace('" updates="', ' ').replace('"/>', '')
                list = str.split()
                id = list[0]
                cab_file = open(f'{self.folder}/new_{id}.txt', "r")
                for j, cab_line in enumerate(cab_file):
                    cab_list = cab_line.split()

                    # Is the cab occupied?
                    if cab_list[2] == '1':
                        if not recording_trajectory:
                            # new trajectory
                            recording_trajectory = True
                            trajectory_id += 1

                        date_time = datetime.fromtimestamp(int(cab_list[3]))
                        writer.writerow([cab_list[0], cab_list[1], date_time.strftime("%Y/%m/%d %H:%M:%S"), trajectory_id])

                    else:
                        if recording_trajectory:
                            # We finished to record a trajectory
                            recording_trajectory = False
                            num_trajectories += 1
                            if num_trajectories == max_trajectories:
                                cab_file.close()
                                main_file.close()
                                return
                cab_file.close()
            main_file.close()
