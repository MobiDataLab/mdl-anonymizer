from abc import abstractmethod

from mob_data_anonymizer.entities.Dataset import Dataset


class AnonymizationMethodInterface:

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def get_anonymized_dataset(self) -> Dataset:
        pass
