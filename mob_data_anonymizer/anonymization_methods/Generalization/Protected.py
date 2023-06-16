import collections
import itertools
import logging
import math

import pandas as pd
from geopandas import GeoDataFrame
from haversine import haversine, Unit
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
    "strategy": 'avg'
}


def generate_sequences(df: TrajDataFrame):
    traj_sequences = {}
    for index, l in df.iterrows():
        traj_sequences[l['tid']] = traj_sequences.get(l['tid'], []) + [l['tile_ID']]

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
    new_sequences = {}
    for tid in tqdm(sequences, disable=(not show_progress)):
        sequence = sequences[tid]

        # If this trajectory has unique combinations
        if tid in bad_combinations:
            uniq_combs = bad_combinations[tid]

            while uniq_combs:
                # Look for the most common tile in unique combinations
                tmp = list(map(lambda x: x.split("_"), uniq_combs))
                all_tiles = [x for sublist in tmp for x in sublist]

                # Count the occurrences of all tiles
                counter = collections.Counter(all_tiles)
                d = collections.defaultdict(list)
                for k, v in counter.items():
                    d[v].append(k)
                lmc = counter.most_common()
                most_common_tile, count = lmc[0]

                # Check if there are other tiles with the same number of occurrences (a draw)
                # If there are more than 0 tile with the same number of occurrences and trajectory has good combinations
                if len(d[count]) > 1 and tid in good_combinations:

                    # We should decide what tile to remove
                    candidates = d[count]

                    # We'll remove the tile within less good combinations
                    tmp_good = list(map(lambda x: x.split("_"), good_combinations[tid]))
                    all_tiles_good = [x for sublist in tmp_good for x in sublist]

                    min_count = 99999
                    for c in candidates:
                        if all_tiles_good.count(c) < min_count:
                            most_common_tile = c

                # Remove this tile from the original sequence
                sequence = [t for t in sequence if t != most_common_tile]

                # Remove combinations with this tile
                uniq_combs = [x for x in uniq_combs if most_common_tile not in x.split("_")]

        new_sequences[tid] = sequence

    return new_sequences


def mark_locations_to_keep(df: TrajDataFrame, sequences: list[str]):
    def check_trajectory(df1, seq):
        seq_index = -1
        current = None
        for index, row in df1.iterrows():

            if current == row['tile_ID'] or seq_index < len(seq) - 1 and row['tile_ID'] == seq[seq_index + 1]:
                df1.at[index, 'keep'] = True
                if current != row['tile_ID']:
                    seq_index += 1

                current = row['tile_ID']

        return df1['keep']

    df['keep'] = False

    for tid in df['tid'].unique():
        if tid in sequences.keys():
            s = check_trajectory(df[df['tid'] == tid], sequences[tid])
            df.loc[s.index, 'keep'] = s

    return df


def generate_generalized_trajectories_centroid(mtdf: TrajDataFrame, sequences, tiles):
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

    mtdf = mtdf.rename(columns={
        constants.LATITUDE: 'orig_lat',
        constants.LONGITUDE: 'orig_lng',
        'x': constants.LATITUDE,
        'y': constants.LONGITUDE,
    })

    return mtdf


def generate_generalized_trajectories_avg(mtdf, sequences, tiles):

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

    mtdf = pd.merge(mtdf, new_lng, how="left", on="tile_ID", suffixes=('', '_new'))
    mtdf = pd.merge(mtdf, new_lat, how="left", on="tile_ID", suffixes=('', '_new'))

    mtdf = mtdf.rename(columns={
        constants.LATITUDE: 'orig_lat',
        constants.LONGITUDE: 'orig_lng',
        constants.LATITUDE + '_new': constants.LATITUDE,
        constants.LONGITUDE + '_new': constants.LONGITUDE,
    })

    return mtdf


def clean_tdf(mtdf: TrajDataFrame):
    # Rename and reorder columns
    # mtdf.rename(columns={
    #     constants.LATITUDE: 'orig_lat',
    #     constants.LONGITUDE: 'orig_lng',
    #     'x': constants.LONGITUDE,
    #     'y': constants.LATITUDE,
    # }, inplace=True)

    # We want to group locations in the same tile, but just if they are contiguous
    # (not if a user has come back to a previous tile)
    mtdf = mtdf.sort_values(by=[constants.TID, constants.DATETIME])

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
    Check the original tessellation and try to merge cells with less than min_k locations
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

    def merge_tiles(tile_ids: list[str], tessellation: GeoDataFrame):
        '''

        :param tile_ids: Set with the tile ids of the tiles to be combined
        :param tessellation: The whole tessellation
        :return: The whole tessellation with the tiles combined
        '''
        polygons = list(map(lambda id: tessellation[tessellation.tile_ID == id].geometry.values[0], tile_ids))

        new_polygon = unary_union(polygons)

        # Delete rows
        for id in tile_ids:
            tessellation = tessellation.drop(tessellation[tessellation.tile_ID == id].index)

        # Add new row to geoseries
        row = pd.Series([f'{".".join(sorted(tile_ids))}', new_polygon, None, None, None], index=tessellation.columns)

        tessellation = pd.concat([tessellation, row.to_frame().T], ignore_index=True)

        return tessellation

    rows, columns = get_grid_shape(tiles)
    max_tile_id = (rows * columns) - 1

    # Count the number of locations in every tile
    s = mtdf['tile_ID'].value_counts()
    tiles = pd.merge(tiles, s, left_on="tile_ID", right_index=True)
    tiles = tiles.rename(columns={
        'tile_ID_y': 'n_locs',
    })
    tiles = tiles.drop('tile_ID_x', axis="columns")

    # Compute centroids of the tiles as avg of locations
    mtdf_tiles = pd.merge(mtdf, tiles, how="left", on="tile_ID")
    new_lng = mtdf_tiles.groupby('tile_ID', as_index=False)[constants.LONGITUDE].mean()
    new_lat = mtdf_tiles.groupby('tile_ID', as_index=False)[constants.LATITUDE].mean()
    tiles = pd.merge(tiles, new_lng, how="left", on="tile_ID")
    tiles = pd.merge(tiles, new_lat, how="left", on="tile_ID")

    # Get tiles with less than 2*k locations
    tiles_to_check = tiles[tiles['n_locs'] < min_k]
    tiles_to_check = tiles_to_check.sort_values(by=['n_locs', 'tile_ID'])

    # We start to try to join tiles
    tiles_to_join = []      # List of sets with the ids to be joined

    for index, tile in tiles_to_check.iterrows():
        tile_id = int(tile['tile_ID'])
        tile_lat = tile['lat']
        tile_lng = tile['lng']

        # Look the four adjacents files
        tile_up = tile_id + 1 if (tile_id + 1) % rows != 0 else None
        tile_down = tile_id - 1 if tile_id % rows != 0 else None
        tile_left = tile_id - rows if tile_id - rows >= 0 else None
        tile_right = tile_id + rows if tile_id + rows < max_tile_id else None

        candidate_ids = (tile_up, tile_right, tile_down, tile_left)

        max_gravity = 0
        selected_tile = None
        selected_id = None
        for candidate_id in candidate_ids:
            row = tiles[tiles.tile_ID == str(candidate_id)]

            if not row.empty:
                row_lat = row['lat'].iloc[0]
                row_lng = row['lng'].iloc[0]
                # Compute gravity
                d = haversine((tile_lat, tile_lng), (row_lat, row_lng))
                locs = row['n_locs'].iloc[0]
                g = locs / (d ** 2)

                # The tile will be merged with the adjacent tile which 'attracts' it more
                if g > max_gravity:
                    max_gravity = g
                    selected_tile = row
                    selected_id = candidate_id

        if selected_tile is not None:

            # Add to tiles to join
            for group in tiles_to_join:
                # If one of the tiles has been market to be joined before, we add a new tile to this set
                if not group.isdisjoint({tile_id, selected_id}):
                    group |= {str(tile_id), str(selected_id)}
                    break
            else:
                # Otherwise, we create a new set of tiles to be joined
                tiles_to_join.append({str(tile_id), str(selected_id)})

    # Merge all the sets to get disjoint supersets
    tiles_to_join = get_super_sets(tiles_to_join)

    for s in tiles_to_join:
        tiles = merge_tiles(s, tiles)

    return tiles


class ProtectedGeneralization(AnonymizationMethodInterface):

    def __init__(self, dataset: Dataset, tile_size: int = DEFAULT_VALUES['tile_size'],
                 k: int = DEFAULT_VALUES['k'], knowledge: int = DEFAULT_VALUES['knowledge'],
                 strategy: str = DEFAULT_VALUES['strategy']):
        self.dataset = dataset
        self.anonymized_dataset = dataset.__class__()

        self.tile_size = tile_size
        self.k = k
        self.knowledge = knowledge
        self.strategy = strategy

    def run(self):
        tdf = self.dataset.to_tdf()

        logging.info("Starting tessellation")
        mtdf, tessellation = spatial_tessellation(tdf, "squared", self.tile_size)

        logging.info("Preprocessing tiles")
        tessellation = preprocessing_merge_tiles(tessellation, mtdf, 2 * self.k)

        mtdf = tdf.mapping(tessellation, remove_na=True)

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

        logging.info("Generating sequences")
        if self.strategy == 'centroid':
            mtdf = generate_generalized_trajectories_centroid(mtdf, sequences, tessellation)
        else:
            mtdf = generate_generalized_trajectories_avg(mtdf, sequences, tessellation)

        # mtdf.to_csv(f"filtered_dataset_20080608_tmp_k{self.k}_kw{self.knowledge}_t{self.tile_size}.csv")
        logging.info("Cleaning TDF")
        mtdf = clean_tdf(mtdf)

        logging.info(f"Finished! Anonymized dataset has {len(mtdf)} locations")
        self.anonymized_dataset.from_tdf(mtdf)

    def get_anonymized_dataset(self) -> Dataset:
        return self.anonymized_dataset
