import logging
import pandas as pd
from skmob.utils import constants
from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.anonymization_methods.SwapLocations.trajectory_anonymization import \
    apply_trajectory_anonymization
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.tessellation import spatial_tessellation

DEFAULT_VALUES = {
    "gen_tile_size": 500,
    "tile_shape": "squared",
    "traj_anon_tile_size": 1000,
    "overlapping_strategy": "all"      # Options: "all", "one"
}


class SimpleGeneralization(AnonymizationMethodInterface):
    def __init__(self, dataset: Dataset,
                 gen_tile_size=DEFAULT_VALUES['gen_tile_size'], tile_shape=DEFAULT_VALUES["tile_shape"],
                 traj_anon_tile_size=DEFAULT_VALUES["traj_anon_tile_size"],
                 overlapping_strategy=DEFAULT_VALUES['overlapping_strategy']):
        self.dataset = dataset
        self.anonymized_dataset = dataset.__class__()

        self.gen_tile_size = gen_tile_size
        self.traj_anon_tile_size = traj_anon_tile_size
        self.tile_shape = tile_shape
        self.overlapping_strategy = overlapping_strategy

    def run(self):
        pd.set_option('display.max_columns', None)
        tdf_dataset = self.dataset.to_tdf()

        mtdf, tiles = spatial_tessellation(tdf_dataset, self.tile_shape, self.gen_tile_size)
        # print(mtdf.head(5))
        # print(tiles.head(5))

        tiles['x'] = round(tiles['geometry'].centroid.x, 5)
        tiles['y'] = round(tiles['geometry'].centroid.y, 5)

        # Add tiles centroids to mapped tdf
        mtdf = pd.merge(mtdf, tiles, how="left", on="tile_ID")

        # Rename and reorder columns
        mtdf.rename(columns={
            constants.LATITUDE: 'orig_lat',
            constants.LONGITUDE: 'orig_lng',
            'x': constants.LONGITUDE,
            'y': constants.LATITUDE,
        }, inplace=True)

        mtdf = mtdf[
            [constants.LONGITUDE, constants.LATITUDE, constants.DATETIME, constants.UID, constants.TID]]

        if self.overlapping_strategy == "one":
            # If two or more locations of the same trajectory are in the same tile, keep just one with the avg timestamp
            mtdf = mtdf.groupby([constants.TID, constants.UID, constants.LATITUDE, constants.LONGITUDE],
                                as_index=False).mean()

        mtdf.to_csv("anonymized_pre.csv")
        logging.info(f"Anonymized dataset has {len(mtdf)} locations before trajectory anonymization")
        mtdf = apply_trajectory_anonymization(mtdf, tile_size=self.traj_anon_tile_size)
        logging.info(f"Anonymized dataset has {len(mtdf)} locations")
        self.anonymized_dataset.from_tdf(mtdf)

    def get_anonymized_dataset(self):
        return self.anonymized_dataset
