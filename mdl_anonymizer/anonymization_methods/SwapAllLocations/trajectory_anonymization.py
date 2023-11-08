import logging

import pandas
from haversine import haversine, Unit
from more_itertools import pairwise

from mdl_anonymizer.utils.tessellation import spatial_tessellation

tessellation_shape_type = "squared"


def apply_trajectory_anonymization(tdf, tile_size: int = 1000):
    '''
    Apply a simple trajectory anonymization method. Use when you have previously anonymized a dataset at location level.
    :return:
    '''

    logging.info("Creating fake locations")
    # Distance between consecutive locations have to be less than tile size
    temp_tdf = tdf.sort_values(['uid', 'tid', 'datetime'])

    # Copy the data of the previous locations in new columns
    temp_tdf['p_tid'] = temp_tdf['tid'].shift(1)
    temp_tdf['p_lng'] = temp_tdf['lng'].shift(1)
    temp_tdf['p_lat'] = temp_tdf['lat'].shift(1)
    temp_tdf['p_datetime'] = temp_tdf['datetime'].shift(1)

    fake_locations = []
    for index, l in temp_tdf.iterrows():
        distance = haversine((l['lat'], l['lng']), (l['p_lat'], l['p_lng']), unit=Unit.METERS)
        if l['tid'] == l['p_tid'] and distance >= tile_size:
            # We create a list fake locations with just the timestamp (we interpolate the position later)
            n_fakes = int(distance / tile_size)
            for i in range(1, n_fakes + 1):
                new_timestamp = l['p_datetime'] + (i * (l['datetime'] - l['p_datetime']) / (n_fakes + 1))
                fake_locations.append([l['uid'], l['tid'], None, None, new_timestamp])

    # Data frame with just the fake locations to be computed
    fl_df = pandas.DataFrame(fake_locations, columns=['uid', 'tid', 'lng', 'lat', 'datetime'])

    # Concat the original dataframe and the fake locations dataframe
    fl_tdf = pandas.concat([tdf, fl_df], axis=0, ignore_index=True)
    fl_tdf.sort_values(['uid', 'tid', 'datetime'], inplace=True, ignore_index=True)

    # Interpolate the missing positions
    fl_tdf[['lng', 'lat']] = fl_tdf[['lng', 'lat']].interpolate()

    logging.info(f"{len(fake_locations)} new fake locations created")
    logging.info(f"Tessellating")
    # Tessellate both the original dataframe and the datafram with fake locations
    mfl_tdf, tessellation = spatial_tessellation(fl_tdf, tiles_shape="squared", meters=tile_size)
    mtdf, tessellation = spatial_tessellation(tdf, tiles=tessellation)

    # Compute tile sequences of the tdf with fake locations
    logging.info("Computing tile sequences")
    traj_sequences = {}

    for index, l in mfl_tdf.iterrows():
        try:
            if l['tile_ID'] not in traj_sequences[l['tid']]:
                traj_sequences[l['tid']].append(l['tile_ID'])
        except KeyError:
            traj_sequences[l['tid']] = [l['tile_ID']]

    # Count sub_sequences ocurrences
    logging.info("Counting pairwise occurrences")
    subseq_count = {}

    for traj_id in traj_sequences:
        # print(traj_sequences[traj_id])
        # print(list(more_itertools.substrings(traj_sequences[traj_id])))
        if len(traj_sequences[traj_id]) > 1:
            for sub_seq in pairwise(traj_sequences[traj_id]):
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

    # We remove the locations from pairwise tiles that just appear one time
    logging.info("Removing locations")

    # We iterate over the sub sequences sorted by the number of occurrences (descending). So, first, we keep all the
    # tiles to be preserved
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
                    # print(f'Removing: traj_id {tid} tile_id {tile}')
                    # print(mtdf[(mtdf.tid == tid) & (mtdf.tile_ID == tile)].index)
                    mtdf.drop(mtdf[(mtdf.tid == tid) & (mtdf.tile_ID == tile)].index, inplace=True)

    # tessellation.to_csv("tiles.csv")

    mtdf = mtdf.drop('tile_ID', axis=1).reset_index(drop=True)

    return mtdf
