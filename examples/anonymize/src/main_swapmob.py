import logging
import time

from src.anonymization_methods.SwapMob.SwapMob import SwapMob
from src.entities.Dataset import Dataset
from src.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

dataset = Dataset()
dataset_name = "cabs_dataset_20080608_0800_1000"
dataset.load_from_scikit(f'../../data/{dataset_name}.csv', min_locations=10, datetime_key="timestamp")
dataset.filter_by_speed()
dataset.export_to_scikit(filename="../out/actual_dataset_loaded.csv")

temporal_thold=30
spatial_thold=0.5
min_n_swaps=1

anonymizer = SwapMob(dataset, temporal_thold=temporal_thold, spatial_thold=spatial_thold, min_n_swaps=min_n_swaps, seed=42)
ini_t = time.time()
anonymizer.run()
logging.info(f"Anonymization time = {time.time()-ini_t} seconds")
anon_dataset = anonymizer.get_anonymized_dataset()

anon_dataset.set_description("DATASET ANONYMIZED")

anon_dataset.export_to_scikit(filename="../out/cabs_scikit_anonymized.csv")
anon_dataset.export_to_scikit(filename=f"../out/{dataset_name}_anon_swapmob_t{temporal_thold}_s{spatial_thold}_m{min_n_swaps}.csv")

stats = Stats(dataset, anon_dataset)
print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')