from mdl_anonymizer.measures_methods.MeasuresMethodInterface import MeasuresMethodInterface
from mdl_anonymizer.entities.Dataset import Dataset

DEFAULT_VALUES = {
    
}


class TrajectoriesRemoved(MeasuresMethodInterface):
    def __init__(self, original_dataset: Dataset, anom_dataset: Dataset):
        self.original_dataset = original_dataset
        self.anom_dataset = anom_dataset
        self.results = {}

    def run(self):
        self.results["percen_traj_removed"] = round(self.get_perc_of_removed_trajectories() * 100, 2)
        self.results["percen_loc_removed"] = round(self.get_perc_of_removed_locations() * 100, 2)

    def get_result(self):
        return self.results

    def get_number_of_removed_trajectories(self):
        return len(self.original_dataset) - len(self.anom_dataset)

    def get_number_of_removed_locations(self):
        return self.original_dataset.get_number_of_locations() - self.anom_dataset.get_number_of_locations()

    def get_perc_of_removed_trajectories(self):
        return self.get_number_of_removed_trajectories() / len(self.original_dataset)

    def get_perc_of_removed_locations(self):
        return self.get_number_of_removed_locations() / self.original_dataset.get_number_of_locations()
