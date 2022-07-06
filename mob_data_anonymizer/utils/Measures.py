import logging
from shapely import geometry
from geopandas import GeoDataFrame
import pandas
from sklearn.metrics import mean_squared_error

from skmob import TrajDataFrame
from skmob.measures.collective import mean_square_displacement, random_location_entropy, uncorrelated_location_entropy, \
    visits_per_location
from skmob.measures.individual import distance_straight_line
from skmob.tessellation import tilers
from skmob.utils.constants import DEFAULT_CRS

from mob_data_anonymizer.utils.tessellation import tessellate


class Measures:
    def __init__(self, original_tdf: TrajDataFrame, anonymized_tdf: TrajDataFrame, sort=True, tesselation_meters=500, output_folder=""):

        self.pre_original_tdf = original_tdf
        self.pre_anonymized_tdf = anonymized_tdf

        if sort:
            # Sorting by timestamp
            logging.info("Sorting original dataset")
            self.pre_original_tdf.sort_values("datetime", inplace=True)

            logging.info("Sorting anoymized dataset")
            self.pre_anonymized_tdf.sort_values("datetime", inplace=True)

        # Tessellation
        logging.info("Tessellating original dataset")
        self.original_tdf = tessellate(self.pre_original_tdf, "h3_tessellation")
        logging.info("Tessellating anonymized dataset")
        self.anonymized_tdf = tessellate(self.pre_anonymized_tdf, "h3_tessellation")
        # bounding_box = self._get_bounding_box(self.pre_original_tdf)
        # tessellation = tilers.tiler.get("squared", base_shape=bounding_box, meters=tesselation_meters)
        #
        # mOrig = self.pre_original_tdf.mapping(tessellation)
        # mAnon = self.pre_anonymized_tdf.mapping(tessellation)



        self.output_folder = output_folder

        self.results = {}



    def __get_bounding_box(tdf):
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

    ### COLLECTIVE

    def cmp_mean_square_displacement(self):
        '''
        (See https://scikit-mobility.github.io/scikit-mobility/reference/collective_measures.html#skmob.measures.collective.mean_square_displacement)
        Returns
        -------

        '''
        logging.info("Computing Mean Square Displacement")

        o = mean_square_displacement(self.original_tdf, show_progress=False)
        a = mean_square_displacement(self.anonymized_tdf, show_progress=False)

        print(f"Mean square displacement: Original={o} - Anonymized={a}")

    def cmp_random_location_entropy(self, output='mean'):
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
            print(f"Average random location entropy: Original={o} - Anonymized={a}")

        if output == 'report':
            report = pandas.merge(dt_o, dt_a, on=["lat", "lng"])
            report.rename(columns={"random_location_entropy_x": "orig", "random_location_entropy_y": "anon"},
                          inplace=True)
            report.to_csv(f"{self.output_folder}Random_location_entropy.csv", index=False)


    def cmp_uncorrelated_location_entropy(self, output='mean'):
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
            print(f"Average uncorrelated location entropy: Original={o} - Anonymized={a}")

        if output == 'report':
            report = pandas.merge(dt_o, dt_a, on=["lat", "lng"])
            report.rename(columns={"uncorrelated_location_entropy_x": "orig", "uncorrelated_location_entropy_y": "anon"},
                          inplace=True)
            report.to_csv(f"{self.output_folder}uncorrelated_location_entropy.csv", index=False)

    def cmp_visits_per_location(self, output='mean'):
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
            print(f"Average visits per location: Original={o} - Anonymized={a}")

        if output == 'report':
            report = pandas.merge(dt_o, dt_a, on=["lat", "lng"])
            report.rename(columns={"n_visits_x": "orig", "n_visits_y": "anon"},
                          inplace=True)
            report.to_csv(f"{self.output_folder}visits_per_location.csv", index=False)

    ### INDIVIDUAL
    def cmp_distance_straight_line(self, output='mean'):
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
            print(f"Average distance straight line: Original={o} - Anonymized={a}")

        if output == 'report':
            report = pandas.merge(dt_o, dt_a, on="uid")
            report.rename(columns={"distance_straight_line_x": "orig", "distance_straight_line_y": "anon"},
                          inplace=True)
            report.to_csv(f"{self.output_folder}Distance_straight_line.csv", index=False)
