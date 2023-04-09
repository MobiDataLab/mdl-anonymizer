from abc import abstractmethod

from mob_data_anonymizer.entities.Dataset import Dataset


class AnonymizationMethodInterface:

    @staticmethod
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def get_anonymized_dataset(self) -> Dataset:
        pass
