from collections import defaultdict
from math import sqrt

from mob_data_anonymizer.entities.Dataset import Dataset


class Stats:

    def __init__(self, original: Dataset, anonymized: Dataset):
        self.original_dataset = original
        self.anonymized_dataset = anonymized

    def get_number_of_removed_trajectories(self):
        return len(self.original_dataset) - len(self.anonymized_dataset)

    def get_number_of_removed_locations(self):
        return self.original_dataset.get_number_of_locations() - self.anonymized_dataset.get_number_of_locations()

    def get_perc_of_removed_trajectories(self):
        return self.get_number_of_removed_trajectories() / len(self.original_dataset)

    def get_perc_of_removed_locations(self):
        return self.get_number_of_removed_locations() / self.original_dataset.get_number_of_locations()

    def get_rsme(self, distance):
        # TODO: Y como se mide la diferencia cuando una trayectoría ha sido eliminada?
        dist = 0.0
        for t1 in self.original_dataset.trajectories:
            t1_anon = self.anonymized_dataset.get_trajectory(t1.id)
            if t1_anon:
                d = distance.compute(t1, t1_anon)
                if d and d != 9999999999999:
                    dist += pow(d, 2)
        dist /= len(self.anonymized_dataset)
        dist = sqrt(dist)

        return dist

    def get_rsme_ordered(self, distance):
        # TODO: Y como se mide la diferencia cuando una trayectoría ha sido eliminada?
        distance.distance_matrix = defaultdict(dict)
        dist = 0.0
        dist2 = 0
        for i, t1 in enumerate(self.original_dataset.trajectories):
            t1_anon = self.anonymized_dataset.trajectories[i]
            if t1_anon:
                d = distance.compute(t1, t1_anon)
                if d and d != 9999999999999:
                    dist += pow(d, 2)
        dist /= len(self.anonymized_dataset)
        dist = sqrt(dist)

        return dist
