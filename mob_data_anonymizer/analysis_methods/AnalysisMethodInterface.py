from abc import abstractmethod

class AnalysisMethodInterface:

    @staticmethod
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def get_result(self):
        pass

    @abstractmethod
    def export_result(self, filename):
        pass
