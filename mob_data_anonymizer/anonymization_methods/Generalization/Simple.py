import logging
import pandas as pd
from skmob.utils import constants
from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.anonymization_methods.SwapLocations.trajectory_anonymization import \
    apply_trajectory_anonymization
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.tessellation import spatial_tessellation, load_tiles_file, compute_centroids

DEFAULT_VALUES = {
    "tiles_filename": None,
    "tile_size": 500,
    "overlapping_strategy": "all"  # Options: "all", "one"
}


class SimpleGeneralization(AnonymizationMethodInterface):
    """
    SimpleGeneralization anonymization method

    Longer class information....

    Attributes:
        dataset (Dataset): Dataset to be anonymized
        tiles_filename (str): Tiles file for tessellation (geojson or shapefile)
        tile_size (int): If a tiles file is not provided a squared tessellation of size 'tile_size' will be
            generated  (in meters)
        overlapping_strategy (str): If several locations of the same trajectories end up in the same tile, keep all
            ('all') or take just one and compute the average timestamp ('one')
    """

    def __init__(self, dataset: Dataset,
                 tiles_filename: str = DEFAULT_VALUES['tiles_filename'],
                 tile_size: int = DEFAULT_VALUES['tile_size'],
                 overlapping_strategy: str = DEFAULT_VALUES['overlapping_strategy']):

        self.dataset = dataset
        self.anonymized_dataset = dataset.__class__()

        self.tile_size = tile_size
        self.tile_shape = "squared"
        self.overlapping_strategy = overlapping_strategy

        if tiles_filename is not None:
            self.tiles = load_tiles_file(tiles_filename)
        else:
            self.tiles = None

    def run(self):

        tdf_dataset = self.dataset.to_tdf()

        logging.info("\t Tessellating")
        mtdf, tiles = spatial_tessellation(tdf_dataset, tiles=self.tiles, tiles_shape=self.tile_shape,
                                           meters=self.tile_size)
        tiles = compute_centroids(tiles)

        # Add tiles centroids to mapped tdf
        mtdf = pd.merge(mtdf, tiles, how="left", on="tile_ID")

        # Rename and reorder columns
        mtdf = mtdf.rename(columns={
            constants.LATITUDE: 'orig_lat',
            constants.LONGITUDE: 'orig_lng',
            'centroid_lon': constants.LONGITUDE,
            'centroid_lat': constants.LATITUDE,
        })

        mtdf = mtdf[
            [constants.LONGITUDE, constants.LATITUDE, constants.DATETIME, constants.UID, constants.TID]]

        if self.overlapping_strategy == "one":
            # If two or more locations of the same trajectory are in the same tile, keep just one with the avg timestamp
            mtdf = mtdf.groupby([constants.TID, constants.UID, constants.LATITUDE, constants.LONGITUDE],
                                as_index=False).mean()

        logging.info(f"Anonymized dataset has {len(mtdf)} locations")
        self.anonymized_dataset.from_tdf(mtdf)

    def get_anonymized_dataset(self):
        return self.anonymized_dataset
