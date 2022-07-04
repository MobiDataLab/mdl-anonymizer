import logging
import sys
sys.path.append("../../../")

from mob_data_anonymizer.anonymization_methods.MegaSwap.MegaSwap import MegaSwap
from mob_data_anonymizer.distances.trajectory.Martinez2021.Distance import Distance
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

dataset = Dataset()
dataset.load_from_scikit('../data/cabs_dataset_20080608_0800_1000.csv', n_trajectories=2000, min_locations=10, datetime_key="timestamp")
dataset.export_to_scikit(filename="../out/actual_dataset_loaded.csv")
# self.assertEqual(10, len(dataset))

# print(dataset)
# 500 trayectorias: landa =  1.0480570490488479
Martinez2021_distance = Distance(dataset, landa=1.0480570490488479)

# IdeaFeliz2021_distance = IdeaFeliz2021_Distance(dataset)
#
# swap_locations = SwapLocations(dataset, k=10, R_t=60, R_s=1, distance=IdeaFeliz2021_distance)
# swap_locations.run()
# anon_dataset = swap_locations.get_anonymized_dataset()

megaSwap = MegaSwap(dataset, R_t=60, R_s=0.5)
megaSwap.run()
anon_dataset = megaSwap.get_anonymized_dataset()

'''
Idea: reconstruir la trayectoria empezando por el principio, añadiendo la siguiente localización más cercana en el
espacio, pero manteniendo el tiempo de la q era 2ª originalmente y seguir
'''
# for t in anon_dataset:
#     new_locations = []
#     l = t.locations[0]
#     new_locations.append(l)
#     min_d = 9999999
#     min_l = None
#     for l2 in [l3 for l3 in t.locations if l3 != l]:
#         d = l.spatial_distance(l2)
#         if d < min_d:
#             min_d = d
#             min_l = l2
#
#     new_l = TimestampedLocation(l.timestamp, min_l.x, min_l.y)



anon_dataset.set_description("DATASET ANONYMIZED")

anon_dataset.export_to_scikit(filename="../out/cabs_scikit_anonymized.csv")

# print(anon_dataset)

stats = Stats(dataset, anon_dataset)
print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')
# rsme = stats.get_rsme(Martinez2021_distance)
# print(rsme)