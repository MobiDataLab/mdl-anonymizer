import json
import logging

import pandas
import skmob
from skmob.utils import plot

from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation import Microaggregation
from mob_data_anonymizer.distances.trajectory.Martinez2021.Distance import Distance
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.io.scikit import Scikit
from mob_data_anonymizer.utils.Stats import Stats

def plot_cluster(cluster_id, filename="out/cluster.html"):
    cluster = microaggregation.get_clusters()[cluster_id]
    centroid = microaggregation.get_centroids()[cluster_id]

    # Plot centroid
    dataset = Scikit.export_trajectory(centroid)
    tdf_centroid = skmob.TrajDataFrame(dataset, user_id=3, latitude=0, longitude=1, datetime=2)

    map = tdf_centroid.plot_trajectory(max_users=1, max_points=None, zoom=12, weight=3, opacity=0.9, hex_color='#FF0000', tiles='Stamen Toner')

    #Plot cluster
    dataset = []
    for t in cluster:
        traj = Scikit.export_trajectory(t)
        dataset.extend(traj)

    tdf_cluster = skmob.TrajDataFrame(dataset, user_id=3, latitude=0, longitude=1, datetime=2)

    map = tdf_cluster.plot_trajectory(map_f=map, max_points=None, zoom=12, weight=2, opacity=0.9, hex_color='#4ffdff',tiles='Stamen Toner')

    map.save(filename)


############################

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

dataset = Dataset()
dataset.load_from_scikit('../anonymize/data/cabs_dataset_20080608_0800_1200.csv', min_locations=10, datetime_key="timestamp")
dataset.filter_by_speed()
dataset.export_to_scikit(filename="out/actual_dataset_loaded.csv")

Martinez2021_distance = Distance(dataset, landa=0.6506385836188395)
microaggregation = Microaggregation(dataset, k=3, distance=Martinez2021_distance)
microaggregation.run()

anon_dataset = microaggregation.get_anonymized_dataset()
anon_dataset.set_description("DATASET ANONYMIZED - MICROAGGREGATION")
anon_dataset.export_to_scikit(filename="out/cabs_scikit_anonymized_Micro_Martinez.csv")

plot_cluster(cluster_id=0, filename='out/first_cluster.html')

last_cluster_id = list(microaggregation.get_centroids())[-1]
plot_cluster(cluster_id=last_cluster_id, filename='out/last_cluster.html')




# stats = Stats(dataset, anon_dataset)
# print(f'Removed trajectories: {round(stats.get_perc_of_removed_trajectories() * 100, 2)}%')
# print(f'Removed locations: {round(stats.get_perc_of_removed_locations() * 100, 2)}%')
#
# rsme = stats.get_rsme(Martinez2021_distance)
# print(f'RSME: {rsme}')




