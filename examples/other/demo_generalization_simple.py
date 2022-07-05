import logging

from mob_data_anonymizer.anonymization_methods.Generalization.Simple import Simple
from mob_data_anonymizer.anonymization_methods.MegaSwap.MegaDynamicSwap import MegaDynamicSwap
from mob_data_anonymizer.anonymization_methods.MegaSwap.MegaSwap import MegaSwap
from mob_data_anonymizer.anonymization_methods.MegaSwap.MegaSwapOptimized import MegaSwapOptimized
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

out_folder = "out/"

#dataset_to_load = "../data/cabs_dataset_0700_0715.csv"
dataset_to_load = "../data/cabs_dataset_20080608_0700_0715.csv"

filename = dataset_to_load.split('/')[-1]
filename_wo_ext = filename.split('.')[0]

dataset = Dataset()
min_locations = 5
dataset.load_from_scikit(dataset_to_load, min_locations=min_locations, datetime_key="timestamp")
dataset.filter_by_speed()

filtered_filename = f"{out_folder}{filename_wo_ext}_filtered_n{min_locations}.csv"

#generalization_simple dataset.export_to_scikit(filename=filtered_filename)

generalization_simple = Simple(dataset)
generalization_simple.run()
anon_dataset = generalization_simple.get_anonymized_dataset()

anonymized_filename = f"{out_folder}{filename_wo_ext}_anonymized_simple.csv"
anon_dataset.set_description("DATASET ANONYMIZED")
anon_dataset.export_to_scikit(filename=anonymized_filename)

stats = Stats(dataset, anon_dataset)
print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')