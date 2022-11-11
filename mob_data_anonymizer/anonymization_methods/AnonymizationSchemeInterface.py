from abc import abstractmethod

class AnonymizationSchemeInterface:

    @staticmethod
    @abstractmethod
    def run(self):
        pass
