import logging

from mob_data_anonymizer.anonymization_methods.SwapLocations.SwapLocations import SwapLocations
from mob_data_anonymizer.anonymization_methods.SwapLocations.MegaSwap import MegaSwap
from mob_data_anonymizer.anonymization_methods.SwapLocations.MegaSwapOptimized import MegaSwapOptimized
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

out_folder = "output/"

dataset_to_load = "../data/cabs_dataset_0700_0715.csv"

filename = dataset_to_load.split('/')[-1]
filename_wo_ext = filename.split('.')[0]

dataset = Dataset()
min_locations = 5
dataset.load_from_scikit(dataset_to_load, min_locations=min_locations, datetime_key="datetime")
dataset.filter_by_speed()

filtered_filename = f"{out_folder}{filename_wo_ext}_filtered_n{min_locations}.csv"

dataset.export_to_scikit(filename=filtered_filename)


# megaSwap = MegaSwap(dataset, R_t=30, R_s=0.3)

k = 3
max_R_s = 500
max_R_t = 120
min_R_s = 100
min_R_t = 60

megaSwap = SwapLocations(dataset, k=k, max_R_s=max_R_s, max_R_t=max_R_t, min_R_s=min_R_s, min_R_t=min_R_t)
megaSwap.run()
anon_dataset = megaSwap.get_anonymized_dataset()

anonymized_filename = f"{out_folder}{filename_wo_ext}_anonymized_SwapLocations_{k}_{max_R_s}_{max_R_t}_{min_R_s}_{min_R_t}.csv"
anon_dataset.set_description("DATASET ANONYMIZED")
anon_dataset.export_to_scikit(filename=anonymized_filename)

stats = Stats(dataset, anon_dataset)
print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')