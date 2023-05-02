from abc import abstractmethod


class MeasuresMethodInterface:

    @staticmethod
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def get_result(self):
        pass
