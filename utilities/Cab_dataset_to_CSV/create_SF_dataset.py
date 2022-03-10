# read main _cabs.txt file
import csv
import datetime

main_file = open("../data/_cabs.txt", "r")
from_date_time = "2008/06/08 07:00:00"
to_date_time = "2008/06/08 07:30:00"
filename = "../out/cabs_dataset_20080608_0700_0730.csv"

element = datetime.datetime.strptime(from_date_time, "%Y/%m/%d %H:%M:%S")
from_timestamp = datetime.datetime.timestamp(element)

element = datetime.datetime.strptime(to_date_time, "%Y/%m/%d %H:%M:%S")
to_timestamp = datetime.datetime.timestamp(element)


with open(filename, mode='w', newline='') as new_file:
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
        cab_file = open(f'../data/new_{id}.txt', "r")

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

                date_time = datetime.datetime.fromtimestamp(int(cab_list[3]))
                writer.writerow([cab_list[0], cab_list[1], date_time.strftime("%Y/%m/%d %H:%M:%S"), trajectory_id])
                locations_count += 1

            else:
                if recording_trajectory:
                    # We finished to record a trajectory
                    recording_trajectory = False

        cab_file.close()
    main_file.close()
print(f"Dataset created with {trajectory_id} trajectories and {locations_count} locations")
