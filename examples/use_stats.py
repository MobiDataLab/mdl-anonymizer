import logging

from src.entities.Dataset import Dataset
from src.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

original_dataset = Dataset()
original_dataset.load_from_scikit("data/cabs_dataset_0700_0715_filtered_n5.csv", min_locations=1)

anon_dataset = Dataset()
anon_dataset.load_from_scikit("data/cabs_dataset_0700_0715_anonymized_megadynamicswap_3_500_120_100_60.csv",  min_locations=1)

stats = Stats(original_dataset, anon_dataset)