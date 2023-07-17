import logging
from shapely import geometry
from geopandas import GeoDataFrame
import pandas
from sklearn.metrics import mean_squared_error
import warnings

from skmob import TrajDataFrame
from skmob.measures.collective import mean_square_displacement, random_location_entropy, uncorrelated_location_entropy, \
    visits_per_location
from skmob.measures.individual import distance_straight_line
from skmob.tessellation import tilers
from skmob.utils import constants
from skmob.utils.constants import DEFAULT_CRS
from mob_data_anonymizer.measures_methods.MeasuresMethodInterface import MeasuresMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from shapely.errors import ShapelyDeprecationWarning
from mob_data_anonymizer.utils.tessellation import spatial_tessellation, compute_centroids
from mob_data_anonymizer.utils.utils import round_tuple

VALID_METHODS = ['mean_square_displacement',
                 'random_location_entropy',
                 'uncorrelated_location_entropy',
                 'visits_per_location',
                 'distance_straight_line']

VALID_MODES = ['average', 'export']

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)


class ScikitMeasures(MeasuresMethodInterface):
    def __init__(self, original_dataset: Dataset, anom_dataset: Dataset,
                 sort=True, tesselation_meters=250,
                 output_folder=""
                 ):
        self.pre_original_tdf: TrajDataFrame = original_dataset.to_tdf()
        self.pre_anonymized_tdf: TrajDataFrame = anom_dataset.to_tdf()

        self.tile_size = tesselation_meters

        if sort:
            # Sorting by timestamp
            logging.info("Sorting original dataset")
            self.pre_original_tdf.sort_values("datetime", inplace=True)

            logging.info("Sorting anoymized dataset")
            self.pre_anonymized_tdf.sort_values("datetime", inplace=True)

        # Tessellation
        logging.info("Tessellating original dataset")
        self.original_tdf, tiles = spatial_tessellation(self.pre_original_tdf, tiles_shape="squared",
                                                        meters=self.tile_size)
        tiles.to_csv("tiles_mock_test_precentroid.csv")
        tiles = compute_centroids(tiles)
        tiles.to_csv("tiles_mock_test.csv")

        self.original_tdf = pandas.merge(self.original_tdf, tiles, how="left", on="tile_ID")
        self.original_tdf = self.original_tdf.rename(columns={
            constants.LATITUDE: 'orig_lat',
            constants.LONGITUDE: 'orig_lng',
            'centroid_lon': constants.LONGITUDE,
            'centroid_lat': constants.LATITUDE,
        })

        logging.info("Tessellating anonymized dataset")
        self.anonymized_tdf, _ = spatial_tessellation(self.pre_anonymized_tdf, tiles=tiles)

        self.anonymized_tdf = pandas.merge(self.anonymized_tdf, tiles, how="left", on="tile_ID")
        self.anonymized_tdf = self.anonymized_tdf.rename(columns={
            constants.LATITUDE: 'orig_lat',
            constants.LONGITUDE: 'orig_lng',
            'centroid_lon': constants.LONGITUDE,
            'centroid_lat': constants.LATITUDE,
        })

        self.output_folder = output_folder
        self.results = {}

    def run(self):
        self.results["visits_per_location_original"], self.results["visits_per_location_anonymized"] \
            = round_tuple(self.cmp_visits_per_location(), 4)
        # print(f"visits per location: Original={self.results['visits_per_location_original']} - "
        #       f"Anonymized={self.results['visits_per_location_anonymized']}")

        self.results["distance_straight_line_original"], self.results["distance_straight_line_anonymized"] \
            = round_tuple(self.cmp_distance_straight_line(), 4)
        # print(f"Distance straight line: Original={self.results['distance_straight_line_original']} - "
        #       f"Anonymized={self.results['distance_straight_line_anonymized']}")

        self.results["uncorrelated_location_entropy_original"], self.results["uncorrelated_location_entropy_anonymized"] \
            = round_tuple(self.cmp_uncorrelated_location_entropy(), 4)
        # print(f"Uncorrelated location entropy: Original={self.results['uncorrelated_location_entropy_original']} - "
        #       f"Anonymized={self.results['uncorrelated_location_entropy_anonymized']}")

        self.results["random_location_entropy_original"], self.results["random_location_entropy_anonymized"] \
            = round_tuple(self.cmp_random_location_entropy(), 4)
        # print(f"Random location entropy: Original={self.results['random_location_entropy_original']} - "
        #       f"Anonymized={self.results['random_location_entropy_anonymized']}")

        self.results["mean_square_displacement_original"], self.results["mean_square_displacement_anonymized"] \
            = round_tuple(self.cmp_mean_square_displacement(), 4)
        # print(f"Mean square displacement: Original={self.results['mean_square_displacement_original']} - "
        #       f"Anonymized={self.results['mean_square_displacement_anonymized']}")

    def get_result(self):
        return self.results


    ### COLLECTIVE

    def cmp_mean_square_displacement(self):
        '''
        (See https://scikit-mobility.github.io/scikit-mobility/reference/collective_measures.html#skmob.measures.collective.mean_square_displacement)
        Returns
        -------

        '''
        logging.info("Computing Mean Square Displacement")

        o = mean_square_displacement(self.pre_original_tdf, show_progress=False)
        a = mean_square_displacement(self.pre_anonymized_tdf, show_progress=False)

        # print(f"Mean square displacement: Original={o} - Anonymized={a}")

        return o, a

    def cmp_random_location_entropy(self, output='average'):
        '''
        ( See https://scikit-mobility.github.io/scikit-mobility/reference/collective_measures.html#skmob.measures.collective.random_location_entropy)

        Parameters
        ----------
        output : {'average', 'report'}
        Type of output

        '''

        logging.info("Computing random location entropy")

        dt_o = random_location_entropy(self.original_tdf, show_progress=False)
        dt_a = random_location_entropy(self.anonymized_tdf, show_progress=False)

        if output == 'average':
            o = dt_o['random_location_entropy'].mean()
            a = dt_a['random_location_entropy'].mean()
            # print(f"Average random location entropy: Original={o} - Anonymized={a}")

            return o, a

        if output == 'export':
            report = pandas.merge(dt_o, dt_a, on=["lat", "lng"])
            report.rename(columns={"random_location_entropy_x": "orig", "random_location_entropy_y": "anon"},
                          inplace=True)
            report.to_csv(f"{self.output_folder}Random_location_entropy.csv", index=False)

    def cmp_uncorrelated_location_entropy(self, output='average'):
        '''
        ( See https://scikit-mobility.github.io/scikit-mobility/reference/collective_measures.html#skmob.measures.collective.uncorrelated_location_entropy)

        Parameters
        ----------
        output : {'average', 'report'}
        Type of output

        '''

        logging.info("Computing uncorrelated location entropy")

        dt_o = uncorrelated_location_entropy(self.original_tdf, show_progress=False)
        dt_a = uncorrelated_location_entropy(self.anonymized_tdf, show_progress=False)

        if output == 'average':
            o = dt_o['uncorrelated_location_entropy'].mean()
            a = dt_a['uncorrelated_location_entropy'].mean()
            # print(f"Average uncorrelated location entropy: Original={o} - Anonymized={a}")

            return o, a

        if output == 'export':
            report = pandas.merge(dt_o, dt_a, on=["lat", "lng"])
            report.rename(
                columns={"uncorrelated_location_entropy_x": "orig", "uncorrelated_location_entropy_y": "anon"},
                inplace=True)
            report.to_csv(f"{self.output_folder}uncorrelated_location_entropy.csv", index=False)

    def cmp_visits_per_location(self, output='average'):
        '''
        ( See https://scikit-mobility.github.io/scikit-mobility/reference/collective_measures.html#skmob.measures.collective.visits_per_location)

        Parameters
        ----------
        output : {'average', 'report'}
        Type of output

        '''

        logging.info("Computing visits per locations")

        dt_o = visits_per_location(self.original_tdf)
        dt_a = visits_per_location(self.anonymized_tdf)

        if output == 'average':
            o = dt_o['n_visits'].mean()
            a = dt_a['n_visits'].mean()
            # print(f"Average visits per location: Original={o} - Anonymized={a}")

            return o, a

        if output == 'export':
            report = pandas.merge(dt_o, dt_a, on=["lat", "lng"])
            report.rename(columns={"n_visits_x": "orig", "n_visits_y": "anon"},
                          inplace=True)
            report.to_csv(f"{self.output_folder}visits_per_location.csv", index=False)

    ### INDIVIDUAL
    def cmp_distance_straight_line(self, output='average'):
        '''
        ( See https://scikit-mobility.github.io/scikit-mobility/reference/individual_measures.html#skmob.measures.individual.distance_straight_line)

        Parameters
        ----------
        output : {'average', 'report'}
        Type of output

        '''

        logging.info("Computing individual distance straight line")

        dt_o = distance_straight_line(self.pre_original_tdf, show_progress=False)
        dt_a = distance_straight_line(self.pre_anonymized_tdf, show_progress=False)

        if output == 'average':
            o = dt_o['distance_straight_line'].mean()
            a = dt_a['distance_straight_line'].mean()
            # print(f"Average distance straight line: Original={o} - Anonymized={a}")
            return o, a

        if output == 'export':
            report = pandas.merge(dt_o, dt_a, on="uid")
            report.rename(columns={"distance_straight_line_x": "orig", "distance_straight_line_y": "anon"},
                          inplace=True)
            report.to_csv(f"{self.output_folder}Distance_straight_line.csv", index=False)

