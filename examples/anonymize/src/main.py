############################## Imports and initialization ##############################
import logging
import time
import os
import sys

from mob_data_anonymizer.anonymization_methods.SwapLocations.SwapLocations import SwapLocations

sys.path.append("../../../")

from mob_data_anonymizer.anonymization_methods.SwapMob.SwapMob import SwapMob
from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation import Microaggregation
from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation2 import Microaggregation2
from mob_data_anonymizer.distances.trajectory.Martinez2021.Distance import Distance
from mob_data_anonymizer.aggregation.Martinez2021.Aggregation import Aggregation
from mob_data_anonymizer.clustering.MDAV.SimpleMDAV import SimpleMDAV
from mob_data_anonymizer.clustering.MDAV.SimpleMDAVDataset import SimpleMDAVDataset
from mob_data_anonymizer.clustering.MDAV.SimpleMDAV_ant import SimpleMDAV_ant
from mob_data_anonymizer.clustering.MDAV.SimpleMDAVDataset_ant import SimpleMDAVDataset_ant

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

############################## Settings ##############################
### Anonymization method selection and settings ###
# METHOD_NAME = "SwapLocations"  # Options: ["SwapMob", "Microaggregation", "SwapLocations"]
METHOD_NAME = "Microaggregation"  # Options: ["SwapMob", "Microaggregation", "Microaggregation2", "SwapLocations"]
TEMPORAL_THLD = 30  # Only for SwapMob
SPATIAL_THLD = 0.2  # Only for SwapMob
MIN_N_SWAPS = 1  # Only for SwapMob
SEED = 42  # Only for SwapMob
K = 3  # Only for Microaggregation
DISTANCE_LANDA = 1.0480570490488479  # Only for Microaggregation
INTERVAL = 24*60*60 # Only for Microaggregation2 (seconds)

### Paths ###
DATA_FOLDER = os.path.join("..", "..", "data")
# DATASET_NAME = "cabs_dataset_0000_2359.parquet"
# DATASET_NAME = "cabs_dataset_20080608.parquet"
DATASET_NAME = "cabs_dataset_20080608_0800_1200.parquet"
# DATASET_NAME = "cabs_dataset_20080608_0700_0715.csv"
DATASET_PATH = os.path.join(DATA_FOLDER, DATASET_NAME)
OUTPUT_FOLDER = os.path.join("..", "..", "output")
PREPROCESSED_PATH = os.path.join(OUTPUT_FOLDER, f"preprocessed_dataset_byCode.csv")
ANONYMIZED_PATH = os.path.join(OUTPUT_FOLDER, f"anonymized_{METHOD_NAME}_byCode.csv")

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

############################## Load dataset and export filtered ##############################
dataset = Dataset()
dataset.from_file(DATASET_PATH, min_locations=10, datetime_key="timestamp")
# dataset.from_file(DATASET_PATH, min_locations=10, datetime_key="timestamp", sample=100000)
dataset.filter_by_speed()
dataset.to_csv(filename=PREPROCESSED_PATH)

############################## Anonymization ##############################
#### Method initialization ###
if METHOD_NAME == "SwapMob":
    anonymizer = SwapMob(dataset, temporal_thold=TEMPORAL_THLD, spatial_thold=SPATIAL_THLD,
                         min_n_swaps=MIN_N_SWAPS, seed=SEED)
elif METHOD_NAME == "Microaggregation":
    Martinez2021_distance = Distance(dataset, landa=DISTANCE_LANDA)
    aggregation_method = Aggregation
    clustering_method = SimpleMDAV_ant(SimpleMDAVDataset_ant(dataset, Martinez2021_distance, aggregation_method))
    anonymizer = Microaggregation(dataset, k=K, clustering_method=clustering_method,
                                  distance=Martinez2021_distance, aggregation_method=aggregation_method)
elif METHOD_NAME == "Microaggregation2":
    Martinez2021_distance = Distance(dataset, landa=0)
    aggregation_method = Aggregation
    clustering_method = SimpleMDAV(SimpleMDAVDataset(dataset, Martinez2021_distance, aggregation_method))
    anonymizer = Microaggregation2(dataset, k=K, clustering_method=clustering_method,
                                   distance=Martinez2021_distance, aggregation_method=aggregation_method,
                                   interval = INTERVAL)
elif METHOD_NAME == "SwapLocations":
    anonymizer = SwapLocations(dataset)
else:
    raise Exception(f"Method [{METHOD_NAME}] is not available. Options: SwapMob, Microaggregation and SwapLocations")

### Anonymization process ###
ini_t = time.time()
anonymizer.run()
elapsed_time = time.time() - ini_t
logging.info(f"Elapsed time = {elapsed_time} seconds")

anon_dataset = anonymizer.get_anonymized_dataset()
anon_dataset.set_description("DATASET ANONYMIZED")

############################## Export anonymized dataset ##############################
anon_dataset.to_csv(filename=ANONYMIZED_PATH)

############################## Statistics ##############################
stats = Stats(dataset, anon_dataset)
print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')
# print(f'rsme: {round(stats.get_rsme(Martinez2021_distance), 4)}')
Martinez2021_distance = Distance(dataset, landa=DISTANCE_LANDA)
print(f'rsme: {round(stats.get_rsme_ordered(Martinez2021_distance), 4)}')
