import csv
import datetime
import logging

from haversine import haversine, Unit
from tqdm import tqdm

from mdl_anonymizer.entities.Dataset import Dataset

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

input_file = "taxi_february.txt"
output_file = "rome_taxi_dataset_all.csv"

# Number of trajectories to read (None if we want all trajectories)
n_users = None
last_user_data = {}  # Dictionary with user_id:[lat, lng, timestamp, current_trajectory_id]

no_locations = 0

max_timestamp = None

min_time_locations = 30  # min time between locations (just to get less locations than the original file)
min_spatial_distance = 100  # min distance (meters) between locations

max_time_locations = 180  # max time between locations to be considered the same trajectory

traj_id = 0


def far_enough(location_1: list, location_2: list):
    """
    Compute is two locations are far enough depending on the required threshold
    """
    return abs(location_1[2] - location_2[2]) >= min_time_locations and \
           haversine((location_1[0], location_1[1]), (location_2[0], location_2[1]),
                     unit=Unit.METERS) >= min_spatial_distance


with open(output_file, mode="w", newline='') as output:
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["lat", "lon", "datetime", "user_id", "trajectory_id"])

    with open(input_file) as input:

        for i, line in enumerate(tqdm(input)):
            fields = line.rstrip().split(";")

            user_id = fields[0]

            # Trajectories to read
            if n_users is None or user_id in last_user_data or len(last_user_data) < n_users:

                if user_id not in last_user_data:
                    last_user_data[user_id] = [0, 0, 0, traj_id]

                d = fields[1]

                idx = d.find('.')
                if idx != -1:
                    dt_object = datetime.datetime.fromisoformat(d[0:idx])
                else:
                    idx = d.find('+')
                    dt_object = datetime.datetime.fromisoformat(d[0:idx])

                timestamp = datetime.datetime.timestamp(dt_object)

                loc = fields[2][6:-1].rstrip().split(" ")

                t_location = [float(loc[0]), float(loc[1]), timestamp]

                # If new location is from a new trajectory, or is far_enough the previous one, write
                if timestamp - last_user_data[user_id][2] >= max_time_locations:
                    traj_id += 1
                    writer.writerow([t_location[0], t_location[1], dt_object, user_id, traj_id])
                    t_location.append(traj_id)
                    last_user_data[user_id] = t_location
                    no_locations += 1
                # If there is far enough the previous one, write
                elif far_enough(t_location, last_user_data[user_id]):
                    current_traj_id = last_user_data[user_id][3]
                    writer.writerow([t_location[0], t_location[1], dt_object, user_id, current_traj_id])
                    t_location.append(current_traj_id)
                    last_user_data[user_id] = t_location
                    no_locations += 1

                if max_timestamp and timestamp > max_timestamp:
                    exit(f'No_locations: {no_locations}\tLast timestamp: {timestamp}')

print(f'Users: {len(last_user_data)} Trajectories: {traj_id} Locations: {no_locations}')

# Filter trajectories with less than X locations
logging.info("Filtering dataset...")
dataset = Dataset()
dataset.from_file(output_file, min_locations=5, datetime_format="%Y-%m-%d %H:%M:%S")
dataset.filter_by_speed()
dataset.to_csv(output_file)
