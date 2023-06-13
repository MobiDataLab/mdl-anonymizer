import collections
import itertools
import logging

import pandas as pd
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
        tid = combinations[code][1][0]
        if combinations[code][0] < k:
            if tid in bad_combinations:
                bad_combinations[tid].append(code)
            else:
                bad_combinations[tid] = [code]

            number_bad_combs += 1
        else:
            if tid in good_combinations:
                good_combinations[tid].append(code)
            else:
                good_combinations[tid] = [code]

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

                    # Y otra idea: antes de empezar, tras la tessellation, juntar celdas con menos de 2k localizaciones?


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

    return mtdf


def generate_generalized_trajectories_avg(mtdf, sequences, tiles):
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

    mtdf.rename(columns={
        constants.LATITUDE + '_new': 'y',
        constants.LONGITUDE + '_new': 'x',
    }, inplace=True)

    return mtdf


def clean_tdf(mtdf: TrajDataFrame):
    # Rename and reorder columns
    mtdf.rename(columns={
        constants.LATITUDE: 'orig_lat',
        constants.LONGITUDE: 'orig_lng',
        'x': constants.LONGITUDE,
        'y': constants.LATITUDE,
    }, inplace=True)

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
        logging.info("Generating sequences")
        sequences = generate_sequences(mtdf)

        logging.info("Counting combinations")
        combinations_count = count_combinations_appearances(sequences, self.knowledge)

        logging.info("Computing unique combinations by trajectory")
        bad_combinations, good_combinations, number_of_bad_comb = get_combinations_by_trajectory(combinations_count,
                                                                                                 self.k)
        # print(bad_combinations_traj)
        # print(bad_combinations_tile)
        # exit()
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

        logging.info("Cleaning TDF")
        mtdf = clean_tdf(mtdf)

        logging.info(f"Finished! Anonymized dataset has {len(mtdf)} locations")
        self.anonymized_dataset.from_tdf(mtdf)

    def get_anonymized_dataset(self) -> Dataset:
        return self.anonymized_dataset
