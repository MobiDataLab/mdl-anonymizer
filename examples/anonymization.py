import logging

from entities.Dataset import Dataset
from factories.anonymization_method_factory import AnonymizationMethodFactory

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

dataset = Dataset()
dataset.from_file("data/mock_dataset.csv")

params = {
        "tile_size": 500,
        "k": 3,
        "knowledge": 2
    }

method = AnonymizationMethodFactory.get('ProtectedGeneralization', dataset, params = params)
method.run()
a_dataset = method.get_anonymized_dataset()

print(len(a_dataset))
print(a_dataset.get_number_of_locations())
print(a_dataset.get_min_timestamp())
print(a_dataset.get_max_timestamp())
print(a_dataset.get_n_locations_longest_trajectory())
print(a_dataset.trajectories[1].locations[0].x)
print(a_dataset.trajectories[1].locations[0].y)
print(a_dataset.trajectories[1].locations[0].timestamp)
