import csv
import datetime
import logging

from haversine import haversine, Unit
from tqdm import tqdm

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

input_file = "taxi_february.txt"
output_file = "rome_taxi_dataset_all_lighter.csv"

# Number of trajectories to read (None if we want all trajectories)
n_users = None
last_user_locations = {}

no_locations = 0

max_timestamp = None

min_time_locations = 30             # min time between locations (just to get less locations than the original file)
min_spatial_distance = 100           # min distance (meters) between locations

with open(output_file, mode="w", newline='') as output:
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["lat", "lon", "timestamp", "traj_id"])

    with open(input_file) as input:

        for i,line in enumerate(tqdm(input)):
            fields = line.rstrip().split(";")

            user_id = fields[0]

            # Trajectories to read
            if n_users is None or user_id in last_user_locations or len(last_user_locations) < n_users:

                if user_id not in last_user_locations:
                    last_user_locations[user_id] = (0, 0, 0)

                d = fields[1]

                idx = d.find('.')
                if idx != -1:
                    dt_object = datetime.datetime.fromisoformat(d[0:idx])
                else:
                    idx = d.find('+')
                    dt_object = datetime.datetime.fromisoformat(d[0:idx])

                timestamp = datetime.datetime.timestamp(dt_object)

                location = fields[2][6:-1].rstrip().split(" ")
                lat = float(location[0])
                long = float(location[1])

                if timestamp - last_user_locations[user_id][2] >= min_time_locations and \
                        haversine((lat, long), (last_user_locations[user_id][0], last_user_locations[user_id][1]), unit=Unit.METERS) >= min_spatial_distance:
                    writer.writerow([lat, long, timestamp, user_id])
                    last_user_locations[user_id] = (lat, long, timestamp)
                    no_locations += 1

                if max_timestamp and timestamp > max_timestamp:
                    exit(f'No_locations: {no_locations}\tLast timestamp: {timestamp}')
