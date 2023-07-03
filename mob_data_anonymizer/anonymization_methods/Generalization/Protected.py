import collections
import itertools
import logging
import math
from bisect import bisect_left
from datetime import datetime

import numpy as np
import pandas as pd
import pytz
from geopandas import GeoDataFrame
from haversine import haversine, Unit
from pandas import DateOffset
from shapely.ops import unary_union
from skmob import TrajDataFrame
from skmob.utils import constants
from tqdm import tqdm

from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.tessellation import spatial_tessellation

DEFAULT_VALUES = {
    "tile_size": 500,
    "k": 3,
    "knowledge": 2,
    "strategy": 'avg',
    "time_interval": None,
    "time_strategy": 'keep'
}


def generate_sequences(df: TrajDataFrame):
    traj_sequences = {}
    for index, l in df.iterrows():
        traj_sequences[l['tid']] = traj_sequences.get(l['tid'], []) + [str(l['tile_ID'])]

    for tid in traj_sequences.keys():
        seq = traj_sequences[tid]
        traj_sequences[tid] = list([k for k, g in itertools.groupby(seq)])

    return traj_sequences


def count_combinations_appearances(sequences: list[str], length: int):
    combs_count = {}
    for traj_id in sequences:

        if len(sequences[traj_id]) > 1:
            # Get all the combinations of the required length or of trajectory's length
            l = min(length, len(sequences[traj_id]))
            for combs in itertools.combinations(sequences[traj_id], l):
                code = "_".join(map(str, combs))

                s = combs_count.get(code, [0, []])
                if traj_id not in s[1]:
                    s[0] += 1
                    s[1] += [traj_id]
                    combs_count[code] = s

    return combs_count


def get_combinations_by_trajectory(combinations: dict, k):
    '''

    :param combinations:
    :param k:
    :return: tuple (bad_combinations, good_combinations, total number of bad combinations
    '''
    number_bad_combs = 0
    bad_combinations = {}
    good_combinations = {}
    for code in combinations:

        # Is this a bad or good combinations(depending on k)
        if combinations[code][0] < k:
            dict_to_update = bad_combinations
            number_bad_combs += 1
        else:
            dict_to_update = good_combinations

        # Update the data of all the related trajectories
        for tid in combinations[code][1]:
            if tid in dict_to_update:
                dict_to_update[tid].append(code)
            else:
                dict_to_update[tid] = [code]

    return bad_combinations, good_combinations, number_bad_combs


def remove_tiles(sequences: list[str], bad_combinations: dict, good_combinations: dict, show_progress: bool = False):
    def duplicates_preprocessing(seq, seq_good_combs):
        '''
        In case of sequence with duplicated element (loops) a special process is needed before removing tiles
        :return:
        '''

        def parent_combination(c):
            '''
            Compute the parent combination of form '1#3_2#2' -> '1_2'
            :param c:
            :return:
            '''
            tiles = c.split("_")
            parent_tiles = list(map(lambda x: x[:x.find('#')], tiles))
            return "_".join(parent_tiles)

        # Compute a new sequence adding to every tile the number of the occurrence
        # f.e. S=[1,2,3,1] -> S=[1#1, 2#1, 3#1, 1#2]
        new_seq = []
        c = {}
        for tile in seq:
            c[tile] = c.get(tile, 0) + 1
            new_seq.append(f'{tile}#{c[tile]}')

        # Recompute combinations
        new_combs = []
        for combs in itertools.combinations(new_seq, 2):
            code = "_".join(map(str, combs))
            new_combs.append(code)

        # The good combinations of the new sequence are those with parent tile is original good combination
        new_good, new_bad = [], []
        for c in new_combs:
            if parent_combination(c) in seq_good_combs:
                new_good.append(c)
            else:
                new_bad.append(c)

        return new_seq, new_bad, new_good

    def fix_bad_combinations(seq, seq_bad_combinations, seq_good_combinations):

        while seq_bad_combinations:
            # Look for the most common tile in bad combinations
            tmp = list(map(lambda x: x.split("_"), seq_bad_combinations))
            all_tiles = [x for sublist in tmp for x in sublist]

            # Count the occurrences of all tiles
            counter = collections.Counter(all_tiles)
            # d is a dict with the number of occurrences as keys, and a list of tiles as values
            # f.e. {5: [tile1, tile2], 3:[tile3, tile4, tile6], 2: [tile5]}
            d = collections.defaultdict(list)
            for k, v in counter.items():
                d[v].append(k)

            # Get most common tile and number of occurrences
            lmc = counter.most_common()
            most_common_tile, count = lmc[0]

            # Check if there are other tiles with the same number of occurrences (a draw)
            # If there are more than 0 tiles with the same number of occurrences and trajectory has good combinations
            if len(d[count]) > 1 and seq_bad_combinations is not None:

                # We should decide what tile to remove
                candidates = d[count]

                # We'll remove the tile within less good combinations
                tmp_good = list(map(lambda x: x.split("_"), seq_good_combinations))
                all_tiles_good = [x for sublist in tmp_good for x in sublist]

                min_count = 99999
                for c in candidates:
                    if all_tiles_good.count(c) < min_count:
                        most_common_tile = c

            # Remove this tile from the original sequence
            seq = [t for t in seq if t != most_common_tile]
            # Remove combinations with this tile
            seq_bad_combinations = [x for x in seq_bad_combinations if most_common_tile not in x.split("_")]

        return seq

    new_sequences = {}
    for tid in tqdm(sequences, disable=(not show_progress)):

        if tid not in good_combinations:
            # This trajectory does not have any good combination -> Remove everything
            sequence = []
        else:
            sequence = sequences[tid]

            # If this trajectory has bad combinations
            if tid in bad_combinations:

                # Are there duplicated elements in the sequence? This means loops in the trajectory
                if len(sequence) != len(set(sequence)):
                    sequence, bad_combs, good_combs = duplicates_preprocessing(sequence,                                                                               good_combinations.get(tid, None))
                    sequence = fix_bad_combinations(sequence, bad_combs, good_combs)
                    # Keep parent tiles
                    sequence = list(map(lambda x: x[:x.find('#')], sequence))
                    # Remove consecutive duplicates
                    sequence = [i for i, j in itertools.zip_longest(sequence, sequence[1:])
                                if i != j]
                else:
                    sequence = fix_bad_combinations(sequence, bad_combinations[tid], good_combinations.get(tid, None))

        new_sequences[tid] = sequence

    return new_sequences


def mark_locations_to_keep(df: TrajDataFrame, sequences: list[str]):
    def check_trajectory(df1, seq):
        '''
        Check what locations have to be preserved based on the anonymized sequence
        :param df1: Dataframe with the locations of the trajectory
        :param seq: Trajectory sequence
        :return:
        '''
        seq_index = -1
        current = None
        for index, row in df1.iterrows():

            if current == row['tile_ID'] or (seq_index < len(seq) - 1 and str(row['tile_ID']) == seq[seq_index + 1]):
                df1.at[index, 'keep'] = True
                if current != row['tile_ID']:
                    seq_index += 1

                current = row['tile_ID']

        return df1['keep']

    df['keep'] = False

    # Check every trajectory
    for tid in df['tid'].unique():
        if tid in sequences.keys():
            s = check_trajectory(df[df['tid'] == tid], sequences[tid])
            df.loc[s.index, 'keep'] = s

    return df


def generate_generalized_trajectories_centroid(mtdf: TrajDataFrame, sequences, tiles, dt_ranges=None):
    tiles['x'] = round(tiles['geometry'].centroid.x, 5)
    tiles['y'] = round(tiles['geometry'].centroid.y, 5)

    mtdf = pd.merge(mtdf, tiles, how="left", on="tile_ID")

    # Mark locations to keep (those whose tile appears in the new sequences)
    mtdf = mark_locations_to_keep(mtdf, sequences)

    # Remove the others
    mtdf = mtdf.drop(mtdf[~mtdf.keep].index)

    # Remove trajectories with just one location
    s = mtdf['tid'].value_counts()
    mtdf = mtdf[mtdf['tid'].map(s) >= 2]

    if dt_ranges is not None:
        dtr = dt_ranges.strftime("%Y-%m-%d %H:%M:%S").tolist()
        mtdf['new_timestamp'] = mtdf.apply(lambda row: dtr[int(row['time_level'])], axis=1)

        mtdf = mtdf.rename(columns={
            constants.DATETIME: 'orig_datetime',
            'new_timestamp': constants.DATETIME,
        })
        mtdf[constants.DATETIME] = pd.to_datetime(mtdf[constants.DATETIME])

    mtdf = mtdf.rename(columns={
        constants.LATITUDE: 'orig_lat',
        constants.LONGITUDE: 'orig_lng',
        'x': constants.LONGITUDE,
        'y': constants.LATITUDE,
    })

    return mtdf


def generate_generalized_trajectories_avg(mtdf, sequences, tiles, dt_ranges=None):
    # Remove some columns from tiles file and merge with mtdf
    tiles = tiles.drop(['n_locs', 'lng', 'lat'], axis="columns", errors="ignore")
    mtdf = pd.merge(mtdf, tiles, how="left", on="tile_ID")

    # Mark locations to keep (those whose tile appears in the new sequences)
    mtdf = mark_locations_to_keep(mtdf, sequences)

    # Remove the others
    mtdf = mtdf.drop(mtdf[~mtdf.keep].index)

    # Remove trajectories with just one location
    s = mtdf['tid'].value_counts()
    mtdf = mtdf[mtdf['tid'].map(s) >= 2]

    new_lng = mtdf.groupby('tile_ID', as_index=False)[constants.LONGITUDE].mean()
    new_lat = mtdf.groupby('tile_ID', as_index=False)[constants.LATITUDE].mean()

    if dt_ranges is not None:
        dtr = dt_ranges.strftime("%Y-%m-%d %H:%M:%S").tolist()
        mtdf['new_timestamp'] = mtdf.apply(lambda row: dtr[int(row['time_level'])], axis=1)


    mtdf = pd.merge(mtdf, new_lng, how="left", on="tile_ID", suffixes=('', '_new'))
    mtdf = pd.merge(mtdf, new_lat, how="left", on="tile_ID", suffixes=('', '_new'))

    mtdf = mtdf.rename(columns={
        constants.LATITUDE: 'orig_lat',
        constants.LONGITUDE: 'orig_lng',
        constants.LATITUDE + '_new': constants.LATITUDE,
        constants.LONGITUDE + '_new': constants.LONGITUDE,
    })

    if dt_ranges is not None:
        mtdf = mtdf.rename(columns={
            constants.DATETIME: 'orig_datetime',
            'new_timestamp': constants.DATETIME,
        })
        mtdf[constants.DATETIME] = pd.to_datetime(mtdf[constants.DATETIME])

    return mtdf


def clean_tdf(mtdf: TrajDataFrame):
    # We want to group locations in the same tile, but just if they are contiguous
    # (not if a user has come back to a previous tile)

    # Compare the tile_ID with the tile_ID of the previous location
    mtdf['pre_TILE'] = (mtdf['tile_ID'] != mtdf['tile_ID'].shift(1))
    # Boolean can be summed, so with this trick we identify the intra-clusters: locations of the same trajectory
    # in the same tile
    mtdf['cum_sum'] = mtdf['pre_TILE'].cumsum()

    mtdf = mtdf[
        [constants.LONGITUDE, constants.LATITUDE, constants.DATETIME, constants.TID, constants.UID, 'cum_sum']]

    # Group intra-clusters by averaging timestamp
    mtdf = mtdf.groupby([constants.TID, constants.UID, constants.LATITUDE, constants.LONGITUDE, 'cum_sum'],
                        as_index=False).mean()

    mtdf = mtdf.sort_values(by=[constants.TID, constants.DATETIME], ignore_index=True)

    mtdf = mtdf[
        [constants.LONGITUDE, constants.LATITUDE, constants.DATETIME, constants.TID, constants.UID]]

    # Remove trajectories with just one location
    s = mtdf[constants.TID].value_counts()
    mtdf = mtdf[mtdf[constants.TID].map(s) >= 2]

    return mtdf


def get_grid_shape(grid: GeoDataFrame):
    '''
    Return the number of rows and columns of a grid geodataframe
    :param tiles:
    :return:
    '''

    t = grid.copy()

    tmp_crs = constants.UNIVERSAL_CRS
    total_area = t.to_crs(tmp_crs)

    cell = GeoDataFrame(index=[0], crs=constants.DEFAULT_CRS, geometry=[t['geometry'][0]])
    cell_area = cell.to_crs(tmp_crs)

    total_boundaries = dict({'min_x': total_area.total_bounds[0],
                             'min_y': total_area.total_bounds[1],
                             'max_x': total_area.total_bounds[2],
                             'max_y': total_area.total_bounds[3]})

    cell_boundaries = dict({'min_x': cell_area.total_bounds[0],
                            'min_y': cell_area.total_bounds[1],
                            'max_x': cell_area.total_bounds[2],
                            'max_y': cell_area.total_bounds[3]})

    total_width = math.fabs(total_boundaries['max_x'] - total_boundaries['min_x'])
    total_height = math.fabs(total_boundaries['max_y'] - total_boundaries['min_y'])

    cell_width = math.fabs(cell_boundaries['max_x'] - cell_boundaries['min_x'])
    cell_height = math.fabs(cell_boundaries['max_y'] - cell_boundaries['min_y'])

    return round(total_height / cell_height), round(total_width / cell_width)


def preprocessing_merge_tiles(tiles: GeoDataFrame, mtdf: TrajDataFrame, min_k: int):
    '''
    Check the original tessellation (3D if we are also tessellating by time) and try to merge cells in the same time_level with less than min_k locations
    :param tiles: original tessellation
    :param mtdf: locations
    :param min_k: min value of locations per cell
    :return:
    '''

    def get_super_sets(list_of_sets: list[set]):
        '''
        Check if some of the sets in the list has some item in common. If that's the case merge the sets in a superset
        :param list_of_sets:
        :return: the list of final supersets
        '''

        if not list_of_sets:
            return []

        while True:
            merged_one = False
            supersets = [list_of_sets[0]]
            for s in list_of_sets[1:]:
                for ss in supersets:
                    if s & ss:
                        ss |= s
                        merged_one = True
                        break
                else:
                    supersets.append(s)

            if not merged_one:
                break

            list_of_sets = supersets

        return supersets

    def merge_tiles(tile_ids: list[str], tdf: TrajDataFrame, tessellation: GeoDataFrame, time_level=0):
        '''

        :param tile_ids: Set with the tile ids of the tiles to be combined
        :param tdf:
        :param tessellation: The whole tessellation
        :param time_level
        :return: The whole tessellation with the tiles combined
        '''

        polygons = list(map(lambda id: tessellation[tessellation.tile_ID == id].geometry.values[0], tile_ids))
        s_tile_ids = list(map(lambda id: tessellation[tessellation.tile_ID == id].s_tile_ID.values[0], tile_ids))
        n_locs = list(
            map(lambda id: tessellation[tessellation.tile_ID == id].n_locs.values[0], tile_ids))

        # New merge tile data
        new_tile_id = f'{".".join(sorted(tile_ids))}'

        new_s_tile_id = f'{".".join(sorted(s_tile_ids))}'
        new_polygon = unary_union(polygons)
        new_n_locs = sum(n_locs)

        # Remap locations
        tdf['tile_ID'] = tdf['tile_ID'].replace(tile_ids, new_tile_id)

        # Add new row to geoseries
        row = pd.Series([new_tile_id, new_polygon, new_s_tile_id, time_level,
                         new_n_locs, None, None], index=tessellation.columns)
        tessellation = pd.concat([tessellation, row.to_frame().T], ignore_index=True)

        # Delete old tiles
        tessellation = tessellation.drop(tessellation[tessellation.tile_ID.isin(tile_ids)].index)

        return tdf, tessellation

    # Get rows, columns and max_tile_id of a spatial layer
    logging.info("\t Computing grid shape")
    rows, columns = get_grid_shape(tiles[tiles['time_level'] == 0])
    logging.info(f"\t Every time layer has {rows} rows and {columns} columns")
    max_tile_id = (rows * columns) - 1

    # Count the number of locations in every tile
    logging.info("\t Counting the number of locations in every tile")
    s = mtdf['tile_ID'].value_counts()
    tiles = pd.merge(tiles, s, left_on='tile_ID', right_index=True)

    tiles = tiles.rename(columns={
        'tile_ID_y': 'n_locs',
    })

    tiles = tiles.drop(['tile_ID_x'], axis=1)

    # Compute centroids of the tiles as avg of locations
    logging.info("\t Computings centroids of the tiles as avg of locations")
    mtdf_tiles = pd.merge(mtdf, tiles, how="left", on="tile_ID")
    new_lng = mtdf_tiles.groupby('tile_ID', as_index=False)[constants.LONGITUDE].mean()
    new_lat = mtdf_tiles.groupby('tile_ID', as_index=False)[constants.LATITUDE].mean()
    tiles = pd.merge(tiles, new_lng, how="left", on="tile_ID")
    tiles = pd.merge(tiles, new_lat, how="left", on="tile_ID")

    # Get tiles with less than 2*k locations
    all_tiles_to_check = tiles[tiles['n_locs'] < min_k]
    all_tiles_to_check = all_tiles_to_check.sort_values(by=['n_locs', 'tile_ID'])

    # Go time level by time level, trying to merging tiles
    logging.info("\t Going time level by time level")
    n_time_levels = all_tiles_to_check['time_level'].unique()
    for t in n_time_levels:
        logging.info(f"\t Time level: {t}")
        time_level_tiles_to_check = all_tiles_to_check[all_tiles_to_check['time_level'] == t].copy()

        # We start to try to join tiles
        logging.info(f"\t\t Building sets of tiles to join")
        tiles_to_join = []  # List of sets with the ids to be joined
        tiles_to_exclude = set()  # During the merge process, the number of locations of the tiles will change. In some cases,
        # tiles originally to be checked can get the min required number of locations,
        # so we will not have to check them

        for index, tile in tqdm(time_level_tiles_to_check.iterrows()):
            tile_id = int(tile['tile_ID'])

            # This tile has been merged before, and it already has the required number of locations
            if tile_id in tiles_to_exclude:
                continue

            s_tile_id = int(tile['s_tile_ID'])
            tile_lat = tile['lat']
            tile_lng = tile['lng']

            # Look the four adjacent tiles (in the same time level)
            tile_up = s_tile_id + 1 if (s_tile_id + 1) % rows != 0 else None
            tile_down = s_tile_id - 1 if s_tile_id % rows != 0 else None
            tile_left = s_tile_id - rows if s_tile_id - rows >= 0 else None
            tile_right = s_tile_id + rows if s_tile_id + rows < max_tile_id else None

            candidate_ids = (tile_up, tile_right, tile_down, tile_left)

            max_gravity = 0
            selected_tile = None
            selected_id = None

            for candidate_id in candidate_ids:

                candidate = tiles[(tiles['s_tile_ID'] == str(candidate_id)) & (tiles['time_level'] == t)]

                if not candidate.empty:
                    row_lat = candidate['lat'].iloc[0]
                    row_lng = candidate['lng'].iloc[0]
                    # Compute gravity
                    d = haversine((tile_lat, tile_lng), (row_lat, row_lng))
                    locs = candidate['n_locs'].iloc[0]
                    g = locs / (d ** 2)

                    # The tile will be merged with the adjacent tile which 'attracts' it more
                    if g > max_gravity:
                        max_gravity = g
                        selected_tile = candidate
                        selected_id = int(candidate['tile_ID'])

            if selected_tile is not None:

                # Add to tiles to join
                for group in tiles_to_join:
                    # If one of the tiles has been marked to be joined before, we add a new tile to this set
                    if not group.isdisjoint({tile_id, selected_id}):
                        group |= {str(tile_id), str(selected_id)}
                        break
                else:
                    # Otherwise, we create a new set of tiles to be joined
                    tiles_to_join.append({str(tile_id), str(selected_id)})

                # If the resulting cell will have more than min_k, mark to not check it
                n_locs = tile['n_locs']
                sel_n_locs = selected_tile['n_locs'].iloc[0]
                if sel_n_locs + n_locs > min_k:
                    tiles_to_exclude.add(selected_id)

        # Merge all the sets to get disjoint supersets
        tiles_to_join = get_super_sets(tiles_to_join)

        logging.info(f"\t\t Merging")
        for s in tqdm(tiles_to_join):
            mtdf, tiles = merge_tiles(s, mtdf, tiles, t)

    return mtdf, tiles


def time_tessellation(tdf: TrajDataFrame, tiles: GeoDataFrame, time_interval: int):
    if not time_interval:
        logging.info('\tNot required')
        tiles['s_tile_ID'] = tiles['tile_ID']
        tiles['time_level'] = 0

        return tdf, tiles, None

    n_tiles = len(tiles)

    # Compute datatime ranges
    datetime_ranges = None

    offset = DateOffset(minutes=time_interval)
    min_datetime = tdf[constants.DATETIME].min()
    max_datetime = tdf[constants.DATETIME].max()

    datetime_ranges = pd.date_range(start=min_datetime, end=max_datetime, freq=offset)
    logging.info(f'\tNumber of time levels: {len(datetime_ranges)}')
    logging.info(f'\tTime levels: {datetime_ranges}')

    # Add temporal tiles to the tessellation
    logging.info('\tAdding temporal tiles')
    tiles['s_tile_ID'] = tiles['tile_ID']
    tiles['tile_ID'] = tiles['tile_ID'].astype('int')
    tiles['s_tile_ID'] = tiles['s_tile_ID'].astype('int')
    tiles['time_level'] = 0

    tiles_2 = tiles.copy()
    for time_level, t in enumerate(tqdm(datetime_ranges)):
        if time_level > 0:
            tiles_2['time_level'] = time_level
            tiles_2['tile_ID'] = tiles_2['s_tile_ID'] + (n_tiles * time_level)
            tiles = pd.concat([tiles, tiles_2], ignore_index=True)

    # Modify tile_Ids based on location timestamp
    logging.info('\tModifying tile ids based on timestamp')
    tdf['tile_ID'] = tdf['tile_ID'].astype('int')
    tdf['tile_ID'] = tdf.apply(
        lambda row: row['tile_ID'] + (
                n_tiles * (bisect_left(datetime_ranges, row[constants.DATETIME]) - 1)),
        axis=1)

    tiles['tile_ID'] = tiles['tile_ID'].astype('str')
    tiles['s_tile_ID'] = tiles['s_tile_ID'].astype('str')
    tdf['tile_ID'] = tdf['tile_ID'].astype('str')

    return tdf, tiles, datetime_ranges


class ProtectedGeneralization(AnonymizationMethodInterface):

    def __init__(self, dataset: Dataset, tile_size: int = DEFAULT_VALUES['tile_size'],
                 time_interval: int = DEFAULT_VALUES['time_interval'],
                 k: int = DEFAULT_VALUES['k'], knowledge: int = DEFAULT_VALUES['knowledge'],
                 strategy: str = DEFAULT_VALUES['strategy'], time_strategy: str = DEFAULT_VALUES['time_strategy']):
        '''

        :param dataset:
        :param tile_size:
        :param time_interval: in minutes
        :param k:
        :param knowledge:
        :param strategy: 'avg' or 'centroid'
        :param time_strategy: 'same' or 'keep'
        '''

        self.dataset = dataset
        self.anonymized_dataset = dataset.__class__()

        self.tile_size = tile_size
        self.time_interval = time_interval
        self.k = k
        self.knowledge = knowledge
        self.strategy = strategy
        self.time_strategy = time_strategy

    def run(self):
        tdf = self.dataset.to_tdf()

        logging.info("Starting tessellation")
        mtdf, tessellation = spatial_tessellation(tdf, "squared", self.tile_size)
        logging.info(f"Number of tiles: {len(tessellation)}")

        logging.info("Time tessellation")
        mtdf, tessellation, datetime_ranges = time_tessellation(mtdf, tessellation, self.time_interval)
        logging.info(f"Number of tiles: {len(tessellation)}")

        logging.info("Preprocessing tiles")
        mtdf, tessellation = preprocessing_merge_tiles(tessellation, mtdf, 3 * self.k)

        logging.info("Generating sequences")
        sequences = generate_sequences(mtdf)

        logging.info("Counting combinations")
        combinations_count = count_combinations_appearances(sequences, self.knowledge)

        logging.info("Computing unique combinations by trajectory")
        bad_combinations, good_combinations, number_of_bad_comb = get_combinations_by_trajectory(combinations_count,
                                                                                                 self.k)
        logging.info(f'Total combinations: {len(combinations_count.keys())}. Bad: {number_of_bad_comb}')

        logging.info("REMOVING TRAJECTORY TILES")
        while number_of_bad_comb > 0:
            logging.info("Starting iteration")
            logging.info("\tStarting removing")

            sequences = remove_tiles(sequences, bad_combinations, good_combinations)

            logging.info("\tCounting combinations")
            combinations_count = count_combinations_appearances(sequences, self.knowledge)

            logging.info("\tComputing unique combinations by trajectory")
            bad_combinations, good_combinations, number_of_bad_comb = get_combinations_by_trajectory(combinations_count,
                                                                                                     self.k)
            logging.info(f'Total combinations: {len(combinations_count.keys())}. Unique: {number_of_bad_comb}')

        logging.info("Generating anonymized trajectories")
        # Use the datetime ranges if we have to use equal timestamps
        dt_ranges = datetime_ranges if (self.time_interval is not None and self.time_strategy == 'same') else None
        if self.strategy == 'centroid':
            mtdf = generate_generalized_trajectories_centroid(mtdf, sequences, tessellation, dt_ranges)
        else:
            mtdf = generate_generalized_trajectories_avg(mtdf, sequences, tessellation, dt_ranges)

        logging.info("Cleaning dataframe")
        mtdf = clean_tdf(mtdf)

        logging.info(f"Finished! Anonymized dataset has {len(mtdf)} locations")
        self.anonymized_dataset.from_tdf(mtdf)

    def get_anonymized_dataset(self) -> Dataset:
        return self.anonymized_dataset
