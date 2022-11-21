import logging
import os
import time

from mob_data_anonymizer.analysis_methods.QuadTreeHeatMap import QuadTreeHeatMap
from mob_data_anonymizer.entities.Dataset import Dataset

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

DATASET_PATH = "../data/cabs_dataset_0700_0715.parquet"
OUTPUT_FOLDER = "../output/"
PREPROCESSED_PATH = os.path.join(OUTPUT_FOLDER, f"preprocessed_dataset_byCode.csv")
OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, f"quadTreeHeatMap_byCode.json")


if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

dataset = Dataset()
dataset.from_file(DATASET_PATH, min_locations=5, datetime_key="timestamp")
dataset.filter_by_speed()
dataset.to_csv(filename=PREPROCESSED_PATH)

analysis = QuadTreeHeatMap(dataset)

ini_t = time.time()
analysis.run()
elapsed_time = time.time() - ini_t
logging.info(f"Elapsed time = {elapsed_time} seconds")

result = analysis.get_result()
result.to_file(f"{OUTPUT_PATH}", driver="GeoJSON")