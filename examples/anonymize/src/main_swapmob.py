import logging

from src.anonymization_methods.SwapMob.SwapMob import SwapMob
from src.entities.Dataset import Dataset
from src.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

dataset = Dataset()
dataset.load_from_scikit('../data/cabs_dataset_20080608_0800_1000.csv', n_trajectories=2000, min_locations=10, datetime_key="timestamp")
dataset.export_to_scikit(filename="../out/actual_dataset_loaded.csv")

anonymizer = SwapMob(dataset, temporal_thold=60, spatial_thold=0.1)
anonymizer.run()
anon_dataset = anonymizer.get_anonymized_dataset()

anon_dataset.set_description("DATASET ANONYMIZED")

anon_dataset.export_to_scikit(filename="../out/cabs_scikit_anonymized.csv")

stats = Stats(dataset, anon_dataset)
print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')