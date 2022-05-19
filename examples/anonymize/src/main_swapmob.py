############################## Imports ##############################
import logging
import time

from mob_data_anonymizer.anonymization_methods.SwapMob.SwapMob import SwapMob
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

############################## Dataset ##############################
dataset = Dataset()
dataset_name = "cabs_dataset_0700_0715" # Alternatively: "cabs_dataset_20080608_0700_0715"
dataset.load_from_scikit(f'../../data/{dataset_name}.csv', min_locations=10, datetime_key="timestamp")
dataset.filter_by_speed()
dataset.export_to_scikit(filename="../out/actual_dataset_loaded.csv")

############################## Anonymization ##############################
temporal_thold = 30
spatial_thold = 0.2
min_n_swaps = 1
anonymizer = SwapMob(dataset, temporal_thold=temporal_thold, spatial_thold=spatial_thold, min_n_swaps=min_n_swaps,
                     seed=42)
ini_t = time.time()
anonymizer.run()
elapsed_time = time.time() - ini_t
logging.info(f"Elapsed time = {elapsed_time} seconds")

anon_dataset = anonymizer.get_anonymized_dataset()
anon_dataset.set_description("DATASET ANONYMIZED")

############################## Store ##############################
anon_dataset.export_to_scikit(filename="../out/cabs_scikit_anonymized.csv")
anon_dataset.export_to_scikit(
    filename=f"../out/{dataset_name}_anon_swapmob_t{temporal_thold}_s{spatial_thold}_m{min_n_swaps}.csv")

############################## Statistics ##############################
stats = Stats(dataset, anon_dataset)
print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')
