import csv
import logging
from datetime import datetime

from mob_data_anonymizer.entities.Dataset import Dataset

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

MODE_DATE_TIME_INTERVAL = 1
MODE_TIME_INTERVAL = 2

dataset_folder = "../../examples/data/full_SF_cabs_dataset/"
main_file = open(f'{dataset_folder}_cabs.txt', "r")


def build_dataset_dt(from_dt, to_dt, output_filename="out/dataset.csv"):
    element = datetime.strptime(from_dt, "%Y/%m/%d %H:%M:%S")
    from_timestamp = datetime.timestamp(element)

    element = datetime.strptime(to_dt, "%Y/%m/%d %H:%M:%S")
    to_timestamp = datetime.timestamp(element)

    with open(output_filename, mode='w', newline='') as new_file:
        writer = csv.writer(new_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["lat", "lon", "timestamp", "user_id"])
        trajectory_id = 0
        recording_trajectory = False

        locations_count = 0

        for i, line in enumerate(main_file):
            str = line.replace('<cab id="', '').replace('" updates="', ' ').replace('"/>', '')
            list = str.split()
            id = list[0]
            print(id)
            cab_file = open(f'{dataset_folder}new_{id}.txt', "r")

            for j, cab_line in enumerate(cab_file):

                cab_list = cab_line.split()

                # Is the location timestamp between 'from_timestamp' and 'to_timestamp'?
                if not from_timestamp < int(cab_list[3]) < to_timestamp:
                    if recording_trajectory:
                        # We finished to record a trajectory
                        recording_trajectory = False

                    continue

                # Is the cab occupied?
                if cab_list[2] == '1':
                    if not recording_trajectory:
                        # new trajectory
                        recording_trajectory = True
                        trajectory_id += 1

                    date_time = datetime.fromtimestamp(int(cab_list[3]))
                    writer.writerow([cab_list[0], cab_list[1], date_time.strftime("%Y/%m/%d %H:%M:%S"), trajectory_id])
                    locations_count += 1

                else:
                    if recording_trajectory:
                        # We finished to record a trajectory
                        recording_trajectory = False

            cab_file.close()
        main_file.close()

        return trajectory_id, locations_count


def build_dataset_t(from_t, to_t, list_of_days=[], output_filename="out/dataset.csv"):

    def check_time(time_to_check, from_time, to_time):

        if from_time > to_time:
            if time_to_check >= from_time or time_to_check <= to_time:
                return True
        elif from_time < to_time:
            if from_time <= time_to_check <= to_time:
                return True

        return False

    from_time = datetime.strptime(from_t, "%H:%M:%S")
    to_time = datetime.strptime(to_t, "%H:%M:%S")

    with open(output_filename, mode='w', newline='') as new_file:
        writer = csv.writer(new_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["lat", "lon", "timestamp", "user_id"])
        trajectory_id = 0
        recording_trajectory = False

        locations_count = 0

        for i, line in enumerate(main_file):
            str = line.replace('<cab id="', '').replace('" updates="', ' ').replace('"/>', '')
            list = str.split()
            id = list[0]
            print(id)
            cab_file = open(f'{dataset_folder}new_{id}.txt', "r")

            for j, cab_line in enumerate(cab_file):

                cab_list = cab_line.split()

                date_time = datetime.fromtimestamp(int(cab_list[3]))
                time_to_check = datetime.strptime(date_time.strftime("%H:%M:%S"), "%H:%M:%S")

                # Is the location's time between 'from_time' and 'to_time'?
                if not check_time(time_to_check, from_time, to_time):
                    if recording_trajectory:
                        # We finished to record a trajectory
                        recording_trajectory = False

                    continue

                # Is the cab occupied?
                if cab_list[2] == '1':
                    if not recording_trajectory:
                        # new trajectory
                        recording_trajectory = True
                        trajectory_id += 1

                    date_time = datetime.fromtimestamp(int(cab_list[3]))
                    # Replace year,month and date. Just preserve time
                    date_time = date_time.replace(year=2022, month=1, day=1)
                    writer.writerow([cab_list[0], cab_list[1], date_time.strftime("%Y/%m/%d %H:%M:%S"), trajectory_id])
                    locations_count += 1

                else:
                    if recording_trajectory:
                        # We finished to record a trajectory
                        recording_trajectory = False

            cab_file.close()
        main_file.close()

        return trajectory_id, locations_count


# mode = MODE_TIME_INTERVAL
#
# if mode == MODE_DATE_TIME_INTERVAL:
#     from_date_time = "2008/06/08 07:00:00"
#     to_date_time = "2008/06/08 07:30:00"
#     output_filename = "out/cabs_dataset_20080608_0700_0730.csv"
#
#     n_trajectories, n_locations = build_dataset_dt(from_date_time, to_date_time, output_filename)
#
#     logging.info(f"Dataset created with {n_trajectories} trajectories and {n_locations} locations")
#
# if mode == MODE_TIME_INTERVAL:
#     from_time = "07:00:00"
#     to_time = "07:15:00"
#     output_filename = "out/cabs_dataset_0700_0715.csv"
#
#     n_trajectories, n_locations = build_dataset_t(from_time, to_time, output_filename=output_filename)
#
#     logging.info(f"Dataset created with {n_trajectories} trajectories and {n_locations} locations")

# Filter the dataset
dataset = Dataset()
dataset.load_from_scikit("../../examples/data/cabs_dataset_all.csv", min_locations=5, datetime_key="timestamp")
dataset.filter_by_speed(max_speed_kmh=150)

filtered_filename = f"out/cabs_dataset_all_filtered_min5loc.csv"

dataset.export_to_scikit(filename=filtered_filename)