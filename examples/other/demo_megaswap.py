import logging

from src.anonymization_methods.MegaSwap.MegaSwap import MegaSwap
from src.anonymization_methods.MegaSwap.MegaSwapOptimized import MegaSwapOptimized
from src.entities.Dataset import Dataset
from src.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

out_folder = "out/"

dataset_to_load = "../data/cabs_dataset_20080608_0700_0715.csv"

filename = dataset_to_load.split('/')[-1]
filename_wo_ext = filename.split('.')[0]

dataset = Dataset()
min_locations = 5
dataset.load_from_scikit('../data/cabs_dataset_20080608_0700_0715.csv', min_locations=min_locations, datetime_key="timestamp")
dataset.filter_by_speed()

filtered_filename = f"{out_folder}{filename_wo_ext}_filtered_n{min_locations}.csv"

dataset.export_to_scikit(filename=filtered_filename)


megaSwap = MegaSwap(dataset, R_t=30, R_s=0.3)
megaSwap.run()
anon_dataset = megaSwap.get_anonymized_dataset()

anonymized_filename = f"{out_folder}{filename_wo_ext}_anonymized_megaswapNotOpt_t30_s300.csv"
anon_dataset.set_description("DATASET ANONYMIZED")
anon_dataset.export_to_scikit(filename=anonymized_filename)

stats = Stats(dataset, anon_dataset)
print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')