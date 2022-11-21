from abc import abstractmethod

class AnonymizationMethodInterface:

    @staticmethod
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def get_anonymized_dataset(self):
        pass
