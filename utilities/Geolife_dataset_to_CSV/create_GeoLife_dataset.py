import csv
import datetime
import os
import time

main_folder = "data\Data"


n_users = 180
n_files_per_user = 0  # 0 = max

output_filename = f"output\dataset_u{n_users}_f{n_files_per_user}.csv"

min_locations_per_trajectory = 5
min_time_locations = 30             # min time between locations (just to get less locations than the original file)
max_time_locations = 120            # max time between locations to be considered the same trajectory

# os.walk()

def write_locations(writer, locations):

    size = len(locations)

    if size >= min_locations_per_trajectory:
        for loc in locations:
            writer.writerow([loc[0], loc[1], loc[2], loc[3], loc[4]])
    else:
        size = None

    locations.clear()

    return size


start_time = time.time()

with open(output_filename, mode='w', newline='') as output:

    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["lat", "lon", "timestamp", "user_id", "traj_id"])

    user_id = 0
    traj_id = 1
    locations_count = 0

    locations_to_write = []

    for (root, dirs, files) in os.walk(main_folder, topdown=True):
        (head, dir) = os.path.split(root)
        if dir.isnumeric():

            user_id += 1
            print(user_id)

        if dir == 'Trajectory':
            n_files = 1
            print(f"\tNumber of files: {len(files)}")
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
                            loc_written = write_locations(writer, locations_to_write)
                            if loc_written:
                                locations_count += loc_written
                                traj_id += 1


                        if timestamp - previous_timestamp >= min_time_locations:
                            locations_to_write.append((lat, long, date_time, user_id, traj_id))
                            #writer.writerow([lat, long, date_time, user_id, traj_id])
                            #locations_count += 1
                            previous_timestamp = timestamp
                    else:
                        #writer.writerow([lat, long, date_time, user_id, traj_id])
                        locations_to_write.append((lat, long, date_time, user_id, traj_id))
                        #locations_count += 1
                        previous_timestamp = timestamp

                loc_written = write_locations(writer, locations_to_write)
                if loc_written:
                    locations_count += loc_written
                    traj_id += 1

                if n_files == n_files_per_user:
                    break

                n_files += 1

            if user_id == n_users:
                break

    output.close()

print(f"Dataset created with {user_id} users, {traj_id-1} trajectories and {locations_count} locations")
print("--- %s seconds ---" % (time.time() - start_time))
