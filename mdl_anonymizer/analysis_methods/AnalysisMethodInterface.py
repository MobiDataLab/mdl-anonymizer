from abc import abstractmethod
from mdl_anonymizer.entities.Dataset import Dataset


class AnalysisMethodInterface:

    @staticmethod
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def get_anonymized_dataset(self) -> Dataset:
        pass

    @abstractmethod
    def get_result(self):
        pass

    @abstractmethod
    def export_result(self, filename):
        pass
