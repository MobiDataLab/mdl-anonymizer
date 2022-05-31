import logging
import numpy as np
import pandas
from sklearn.metrics import mean_squared_error

from skmob import TrajDataFrame
from skmob.measures.collective import mean_square_displacement
from skmob.measures.individual import distance_straight_line



class Measures:
    def __init__(self, original_tdf: TrajDataFrame, anonymized_tdf: TrajDataFrame, sort=True, output_folder=""):

        self.original_tdf = original_tdf
        self.anonymized_tdf = anonymized_tdf

        if sort:
            # Sorting by timestamp
            logging.info("Sorting")
            self.original_tdf.sort_values("datetime", inplace=True)
            self.anonymized_tdf.sort_values("datetime", inplace=True)

        self.output_folder = output_folder

        self.results = {}

    def cmp_mean_square_displacement(self):
        logging.info("Computing Mean Square Displacement")

        o = mean_square_displacement(self.original_tdf, show_progress=False)
        a = mean_square_displacement(self.anonymized_tdf, show_progress=False)

        print("Mean square displacement")
        print(f"Original: {o} - Anonymized: {a}")

    def cmp_distance_straight_line(self, output='mean'):
        '''
        ( See `https://scikit-mobility.github.io/scikit-mobility/reference/individual_measures.html#skmob.measures.individual.distance_straight_line`)

        Parameters
        ----------
        output : {'mean', 'report'}
        Type of output

        '''

        logging.info("Computing individual distance straight line")

        dt_o = distance_straight_line(self.original_tdf, show_progress=False)
        dt_a = distance_straight_line(self.anonymized_tdf, show_progress=False)
        print(dt_o.head())
        if output == 'mean':
            o = dt_o['distance_straight_line'].mean()
            a = dt_a['distance_straight_line'].mean()

            print("Distance straight line (mean)")
            print(f"Original: {o} km - Anonymized: {a} km")

        if output == 'report':
            report = pandas.merge(dt_o, dt_a, on="uid")
            report.rename(columns={"distance_straight_line_x": "orig", "distance_straight_line_y": "anon"}, inplace=True)
            report.to_csv(f"{self.output_folder}Distance_straight_line.csv", index=False)


