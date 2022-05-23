import csv
import datetime
import logging

from tqdm import tqdm

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

input_file = "taxi_february.txt"
output_file = "rome_taxi_dataset_10.csv"

# Number of trajectories to read (None if we want all trajectories)
n_users = 1
timestamp_users = {}

no_locations = 0

max_timestamp = 1391210655

min_time_locations = 10             # min time between locations (just to get less locations than the original file)

with open(output_file, mode="w", newline='') as output:
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["lat", "lon", "timestamp", "traj_id"])

    with open(input_file) as input:

        for i,line in enumerate(tqdm(input)):
            fields = line.rstrip().split(";")

            user_id = fields[0]

            # Trajectories to read
            if n_users is None or user_id in timestamp_users or len(timestamp_users) < n_users:

                if user_id not in timestamp_users:
                    timestamp_users[user_id] = 0

                d = fields[1]
                idx = d.index('.')

                dt_object = datetime.datetime.fromisoformat(d[0:idx])
                timestamp = datetime.datetime.timestamp(dt_object)

                location = fields[2][6:-1].rstrip().split(" ")
                lat = location[0]
                long = location[1]

                if timestamp - timestamp_users[user_id] >= min_time_locations:
                    writer.writerow([lat, long, timestamp, user_id])
                    timestamp_users[user_id] = timestamp
                    no_locations += 1

                if max_timestamp and timestamp > max_timestamp:
                    exit(f'No_locations: {no_locations}\tLast timestamp: {timestamp}')
