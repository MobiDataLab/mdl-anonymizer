import json

import pandas
import skmob
from skmob.utils import plot

from src.anonymization_methods.Microaggregation.Microaggregation import Microaggregation
from src.distances.trajectory.Martinez2021.Distance import Distance
from src.entities.Dataset import Dataset
from src.io.scikit import Scikit
from src.utils.Stats import Stats

dataset = Dataset()
dataset.load_from_scikit('../anonymize/data/cabs_dataset_20080608.csv', n_trajectories=200, min_locations=10, datetime_key="timestamp")
dataset.export_to_scikit(filename="out/actual_dataset_loaded.csv")

Martinez2021_distance = Distance(dataset, landa=1.0480570490488479)
microaggregation = Microaggregation(dataset, k=5, distance=Martinez2021_distance)
microaggregation.run()

anon_dataset = microaggregation.get_anonymized_dataset()
anon_dataset.set_description("DATASET ANONYMIZED - MICROAGGREGATION")
anon_dataset.export_to_scikit(filename="out/cabs_scikit_anonymized_Micro_Martinez.csv")

cluster_0 = microaggregation.get_clusters()[0]
centroid_0 = microaggregation.get_centroids()[0]

# print(json.dumps(cluster_0, sort_keys=True, indent=4, default=str))
# print(centroid_0)

mini_dataset = Scikit.export_trajectory(centroid_0)
for t in cluster_0:
    traj = Scikit.export_trajectory(t)
    mini_dataset.extend(traj)

tdf = skmob.TrajDataFrame(mini_dataset, user_id=3, latitude=0, longitude=1, datetime=2)
plot = tdf.plot_trajectory(zoom=12, weight=3, opacity=0.9, tiles='Stamen Toner')
plot.save('out/first_cluster.html')

last_cluster_id = list(microaggregation.get_centroids())[-1]
cluster_last = microaggregation.get_clusters()[last_cluster_id]
centroid_last = microaggregation.get_centroids()[last_cluster_id]

mini_dataset = Scikit.export_trajectory(centroid_last)
for t in cluster_last:
    traj = Scikit.export_trajectory(t)
    mini_dataset.extend(traj)

tdf = skmob.TrajDataFrame(mini_dataset, user_id=3, latitude=0, longitude=1, datetime=2)
plot = tdf.plot_trajectory(zoom=12, weight=3, opacity=0.9, tiles='Stamen Toner')
plot.save('out/last_cluster.html')





# stats = Stats(dataset, anon_dataset)
# print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
# print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')
#
# rsme = stats.get_rsme(Martinez2021_distance)
# print(f'RSME: {rsme}')




