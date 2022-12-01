import itertools
import logging
import time

import more_itertools
import pandas
import skmob
from geopandas import GeoDataFrame
from haversine import haversine, Unit
from shapely import geometry
from skmob.tessellation import tilers
from skmob.utils.constants import DEFAULT_CRS


def get_bounding_box(tdf):
    # Build bounding box for tesselation
    # Get max, min lat
    max_lat = tdf['lat'].max()
    min_lat = tdf['lat'].min()

    # Get max, min lng
    max_lng = tdf['lng'].max()
    min_lng = tdf['lng'].min()

    point_list = [[max_lng, max_lat], [max_lng, min_lat], [min_lng, min_lat], [min_lng, max_lat]]

    poly = geometry.Polygon(point_list)
    polygon = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[poly])

    return polygon

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

ini_t = time.time()

# squared, voronoi, h3_tessellation
tesellation_type = "squared"
tile_size = 250                     # Meters
file = 'cabs_dataset_20080608_0700_0715.csv'
version = '2'


logging.info("Load file")
# tdf = skmob.TrajDataFrame.from_file(file, latitude='ycoord', longitude='xcoord'
#                                      , datetime='timestamp', user_id='user_id', trajectory_id='trajectory_id')
tdf = skmob.TrajDataFrame.from_file(file, latitude='lat', longitude='lon'
                                    , datetime='timestamp', user_id='user_id', trajectory_id='trajectory_id')

logging.info(f"Dataset with {len(tdf)} locations")

logging.info("Computing bounding box")
bounding_box = get_bounding_box(tdf)

logging.info("Creating fake locations")
# Distance between consecutive locations have to be less than tile size
temp_tdf = tdf.sort_values(['uid', 'tid', 'datetime'])

# print(temp_tdf.head())

# Copy the data of the previous locations in new columns
temp_tdf['p_tid'] = temp_tdf['tid'].shift(1)
temp_tdf['p_lng'] = temp_tdf['lng'].shift(1)
temp_tdf['p_lat'] = temp_tdf['lat'].shift(1)
temp_tdf['p_datetime'] = temp_tdf['datetime'].shift(1)

# print(tdf.loc[tdf['tid'] == 9])
fake_locations = []
for index, l in temp_tdf.iterrows():
    distance = haversine((l['lat'], l['lng']), (l['p_lat'], l['p_lng']), unit=Unit.METERS)
    if l['tid'] == l['p_tid'] and distance >= tile_size:
        # We create fake locations
        n_fakes = int(distance / tile_size)
        for i in range(1, n_fakes+1):
            new_timestamp = l['p_datetime'] + (i * (l['datetime'] - l['p_datetime'])/(n_fakes + 1))
            fake_locations.append([l['uid'], l['tid'], None, None, new_timestamp])

# Data frame with just the fake locations to be computed
fl_df = pandas.DataFrame(fake_locations, columns=['uid', 'tid', 'lng', 'lat', 'datetime'])

# print(fl_df.loc[fl_df['tid'] == 9])

# Concat the original dataframe and the fake locations dataframe
new_tdf = pandas.concat([tdf, fl_df], axis=0, ignore_index=True)
new_tdf.sort_values(['uid', 'tid', 'datetime'], inplace=True, ignore_index=True)

# print(new_df.loc[new_df['tid'] == 9])

# Interpolate the missing locations
new_tdf[['lng', 'lat']] = new_tdf[['lng', 'lat']].interpolate()

# print(new_df.loc[new_df['tid'] == 9])
logging.info(f"Created {len(fake_locations)} new fake locations")

new_tdf.to_csv(f'{file}_fakeLocations_{tesellation_type}_v{version}.csv')


# squared, voronoi, h3_tessellation
logging.info("Tessellating")
tessellation = tilers.tiler.get(tesellation_type, base_shape=bounding_box, meters=tile_size)

# print(tessellation.head())
tessellation.to_csv(f'{file}_tessellation_{tesellation_type}_v{version}.csv')

logging.info("Mapping 1")
m_fl_tdf = new_tdf.mapping(tessellation, remove_na=True)

logging.info("Mapping 2")
mtdf = tdf.mapping(tessellation, remove_na=True)

print(mtdf.dtypes)
exit()

# print(mtdf.head())
# print(len(mtdf))

# Compute tiles sequences

logging.info("Computing tile sequences")
traj_sequences = {}

for index, l in m_fl_tdf.iterrows():
    try:
        if l['tile_ID'] not in traj_sequences[l['tid']]:
            traj_sequences[l['tid']].append(l['tile_ID'])
    except KeyError:
        traj_sequences[l['tid']] = [l['tile_ID']]

# print(traj_sequences)

# Count sub_sequences ocurrences
logging.info("Counting pairwise occurrences")
subseq_count = {}

for traj_id in traj_sequences:
    # print(traj_sequences[traj_id])
    # print(list(more_itertools.substrings(traj_sequences[traj_id])))
    if len(traj_sequences[traj_id]) > 1:
        for sub_seq in itertools.pairwise(traj_sequences[traj_id]):
            code = "_".join(sub_seq)
            # print(code)
            try:
                s = subseq_count[code][1].copy()
                s.add(traj_id)
                subseq_count[code] = (subseq_count[code][0] + 1, s)
            except KeyError:
                subseq_count[code] = (1, {traj_id})
    else:
        code = traj_sequences[traj_id][0]
        try:
            s = subseq_count[code][1].copy()
            s.add(traj_id)
            subseq_count[code] = (subseq_count[code][0] + 1, s)
        except KeyError:
            subseq_count[code] = (1, {traj_id})

# print(subseq_count)

# print(sorted(subseq_count.items(), key=lambda item: item[1][0], reverse=True))

logging.info("Removing locations")

# We iterate over the sub sequences sorted by the number of occurrences (descending)
tiles_to_preserve = {}
for sub_seq_item in sorted(subseq_count.items(), key=lambda item: item[1][0], reverse=True):
    sub_seq = sub_seq_item[0]
    value = sub_seq_item[1]
    n_ocurrences = value[0]
    traj_ids = value[1]
    tiles = sub_seq.split('_')

    if n_ocurrences > 1:
        # Preserve tiles of these trajectories
        for tid in traj_ids:
            for tile in tiles:
                try:
                    tiles_to_preserve[tid].add(tile)
                except KeyError:
                    tiles_to_preserve[tid] = {tile}
    else:
        # Remove locations if tile has not to be preserved
        for tile in tiles:
            tid = list(traj_ids)[0]
            if tid not in tiles_to_preserve.keys() or tile not in tiles_to_preserve[tid]:
                #print(f'Removing: traj_id {tid} tile_id {tile}')
                #print(mtdf[(mtdf.tid == tid) & (mtdf.tile_ID == tile)].index)
                mtdf.drop(mtdf[(mtdf.tid == tid) & (mtdf.tile_ID == tile)].index, inplace=True)

#print(mtdf.head())

mtdf.drop('tile_ID', axis=1)

# print(mtdf.head())
# print(len(mtdf))

mtdf.to_csv(f'{file}_anonymized_{tesellation_type}_v{version}.csv')
logging.info(f"Dataset with {len(mtdf)} locations")

elapsed_time = time.time() - ini_t
logging.info(f"Elapsed time = {elapsed_time} seconds")