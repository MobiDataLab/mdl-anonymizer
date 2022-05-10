import csv
import datetime
import os

main_folder = "data\Data"
output_filename = "output\dataset.csv"

n_users = 2
n_files_per_user = 2  # 0 = max

min_time_locations = 30             # min time between locations (just to get less locations than the original file)
max_time_locations = 120            # max time between locations to be considered the same trajectory

# os.walk()

with open(output_filename, mode='w', newline='') as output:

    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["lat", "lon", "timestamp", "user_id", "traj_id"])

    user_id = 0
    traj_id = 1
    locations_count = 0

    for (root, dirs, files) in os.walk(main_folder, topdown=True):
        (head, dir) = os.path.split(root)
        if dir.isnumeric():

            user_id += 1
            print(user_id)

        if dir == 'Trajectory':
            n_files = 1
            for filename in files:
                previous_timestamp = None
                file = open(os.path.join(root, filename))
                lines = file.readlines()[6:]
                for line in lines:
                    # print(line)
                    location_list = line.rstrip().split(",")
                    lat = location_list[0]
                    long = location_list[1]
                    date_time = location_list[5].replace('-', '/') + ' ' + location_list[6]

                    dt_object = datetime.datetime.strptime(date_time, "%Y/%m/%d %H:%M:%S")
                    timestamp = datetime.datetime.timestamp(dt_object)

                    if previous_timestamp and min_time_locations and max_time_locations:
                        if timestamp - previous_timestamp > max_time_locations:
                            traj_id += 1

                        if timestamp - previous_timestamp >= min_time_locations:
                            writer.writerow([lat, long, date_time, user_id, traj_id])
                            locations_count += 1
                            previous_timestamp = timestamp
                    else:
                        writer.writerow([lat, long, date_time, user_id, traj_id])
                        locations_count += 1
                        previous_timestamp = timestamp

                traj_id += 1

                if n_files == n_files_per_user:
                    break

                n_files += 1

            if user_id == n_users:
                break

print(f"Dataset created with {user_id} users, {traj_id-1} trajectories and {locations_count} locations")
