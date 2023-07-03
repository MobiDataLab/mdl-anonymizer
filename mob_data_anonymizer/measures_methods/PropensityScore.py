import random

from mob_data_anonymizer.measures_methods.MeasuresMethodInterface import MeasuresMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from skmob.tessellation import tilers
import pandas as pd
import numpy as np
from pandas import DateOffset
from datetime import datetime
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score
from bisect import bisect_left
import logging
from tqdm import tqdm
from shapely import geometry
from shapely.ops import transform
from geopandas import GeoDataFrame
import pyproj
from functools import partial
from haversine import haversine, Unit
import math

DEFAULT_VALUES = {
    
}


class PropensityScore(MeasuresMethodInterface):
    def __init__(self, original_dataset: Dataset, anom_dataset: Dataset, tiles_size=200, time_interval=None, seed=None):
        self.original_dataset = original_dataset
        self.anom_dataset = anom_dataset
        self.tiles_size = tiles_size
        self.time_interval = time_interval
        self.results = {}
        self.seed = seed

    def run(self):
        self.results["propensity"] = round(self.get_propensity_score(self.tiles_size, self.time_interval), 4)
        logging.info(f'Propensity score: {self.results["propensity"]}')

    def get_result(self):
        return self.results

    def get_propensity_score(self, tiles_size=200, time_interval=None):

        # Setup seed
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)

        # Compute tessellation and data ranges for the original dataset
        logging.info(f"Tessellation")

        tessellation = tilers.tiler.get("squared", base_shape=self.original_dataset.get_bounding_box(),
                                        meters=tiles_size)
        tessellation['tile_ID'] = pd.to_numeric(tessellation['tile_ID'])

        datetime_ranges = None
        if time_interval:
            logging.info("Time tessellation")
            offset = DateOffset(seconds=time_interval)

            min_datetime = datetime.fromtimestamp(self.original_dataset.get_min_timestamp(),
                                                  self.original_dataset.timezone)
            max_datetime = datetime.fromtimestamp(self.original_dataset.get_max_timestamp(),
                                                  self.original_dataset.timezone)

            datetime_ranges = pd.date_range(min_datetime, max_datetime, freq=offset)

        original_sequences = self.__compute_trajectory_sequences(self.original_dataset, tessellation, datetime_ranges)
        # print('trajectory sequences computed')
        anonymized_sequences = self.__compute_trajectory_sequences(self.anom_dataset, tessellation,
                                                                   datetime_ranges)

        # print('trajectory sequences computed 2')

        # Check the max len of the sequences and repadding if necessary
        max_orig = max([len(original_sequences[i]) for i in original_sequences.keys()])
        max_anon = max([len(anonymized_sequences[i]) for i in anonymized_sequences.keys()])

        if max_orig > max_anon:
            for i in anonymized_sequences.keys():
                anonymized_sequences[i] = [0] * (max_orig - len(anonymized_sequences[i])) + anonymized_sequences[i]

        if max_anon > max_orig:
            for i in original_sequences.keys():
                original_sequences[i] = [0] * (max_anon - len(original_sequences[i])) + original_sequences[i]

        df1 = pd.DataFrame([original_sequences[key] for key in original_sequences.keys()])
        clas = [0] * len(df1)
        df1['clas'] = clas
        df2 = pd.DataFrame([anonymized_sequences[key] for key in anonymized_sequences.keys()])
        clas = [1] * len(df2)
        df2['clas'] = clas
        df = df1.append(df2, ignore_index=True)
        df = shuffle(df)

        train, test = train_test_split(df, random_state=self.seed)
        X_train = train.drop(columns=['clas'])
        y_train = train['clas']
        X_test = test.drop(columns=['clas'])
        y_test = test['clas']
        X_all = df.drop(columns=['clas'])
        y_all = df['clas']

        # model = LogisticRegression()
        # model = GradientBoostingClassifier()
        # model = xgb.XGBClassifier(n_jobs=multiprocessing.cpu_count() // 2)
        # clf = GridSearchCV(model, {'max_depth': [2, 4, 6], 'n_estimators': [50, 100, 200]}, verbose=1, n_jobs=2)
        # clf.fit(X_train, y_train)
        # print(clf.best_score_)
        # print(clf.best_params_)
        # sys.exit(0)

        # clf = LazyClassifier(verbose=0, ignore_warnings=True, custom_metric=None)
        # models, predictions = clf.fit(X_train, X_test, y_train, y_test)
        # print(models)
        # sys.exit(0)

        # model = LogisticRegression()
        model = xgb.XGBClassifier(random_state=self.seed)
        # model = ExtraTreesClassifier()

        model.fit(X_train, y_train)
        preds_train = model.predict(X_train)
        preds_test = model.predict(X_test)
        # print('accuracy in train:', accuracy_score(y_train, preds_train))
        # print('accuracy in test:', accuracy_score(y_test, preds_test))

        preds_all = model.predict(X_all)
        # print('accuracy in all:', accuracy_score(y_all, preds_all))

        # probs = np.max(model.predict_proba(X_all), axis=1)
        probs = model.predict_proba(X_all)[:,1]
        v = 0
        for prob in probs:
            p = (prob - 0.5) ** 2
            v += p
        v /= len(probs)

        return v * 4.0

    def __compute_trajectory_sequences(self, dataset, tessellation, datetime_ranges=None):

        tdf = dataset.to_tdf()

        max_tile_id = tessellation['tile_ID'].max()
        # print(f'MAX tile: {max_tile_id}')
        # Map locations to spatial tiles
        st_tdf = tdf.mapping(tessellation, remove_na=True)

        # Modify tiles_id based on time
        if datetime_ranges is not None:
            st_tdf['tile_ID'] = st_tdf.apply(
                lambda row: row['tile_ID'] + (
                        max_tile_id * (bisect_left(datetime_ranges, row['datetime'].tz_localize("UTC")) - 1)),
                axis=1)

            # Update the max tile id
            max_tile_id = max_tile_id * len(datetime_ranges)
            # print(f'New MAX tile: {max_tile_id}')

        # Scale ids
        tile_ids = st_tdf['tile_ID']
        tile_ids.drop_duplicates(inplace=True)

        new_tile_ids = (tile_ids - 0) / (max_tile_id - 0)

        mapping = pd.Series(new_tile_ids.tolist(), index=tile_ids.tolist()).to_dict()
        st_tdf['tile_ID'] = st_tdf['tile_ID'].map(mapping)

        # Compute tiles sequences
        logging.info("Computing tile sequences")
        sequences = {}

        for index, l in st_tdf.iterrows():
            try:
                if l['tile_ID'] not in sequences[l['tid']]:
                    sequences[l['tid']].append(l['tile_ID'])
            except KeyError:
                sequences[l['tid']] = [l['tile_ID']]

        # Padding

        # max length
        max_length = 0
        for i in sequences.keys():
            if len(sequences[i]) > max_length:
                max_length = len(sequences[i])

        for i in sequences.keys():
            sequences[i] = [0] * (max_length - len(sequences[i])) + sequences[i]

        return sequences

