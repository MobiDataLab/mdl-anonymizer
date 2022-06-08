from skmob import TrajDataFrame

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.tessellation import tessellate


class Simple:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.anonymized_dataset = dataset.__class__()

    def run(self):

        tdf_dataset = self.dataset.to_tdf()

        print(tdf_dataset.head())

        anonymized_tdf = tessellate(tdf_dataset, "h3_tessellation")

        self.anonymized_dataset.from_tdf(anonymized_tdf)

    def get_anonymized_dataset(self):
        return self.anonymized_dataset


