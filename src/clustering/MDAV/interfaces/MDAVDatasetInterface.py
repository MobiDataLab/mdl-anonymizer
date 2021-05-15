from abc import ABC, abstractmethod


class MDAVDatasetInterface(ABC):

    @abstractmethod
    def compute_centroid(self):
        raise NotImplementedError

    @abstractmethod
    def compute_centroid_unselected(self):
        raise NotImplementedError

    @abstractmethod
    def make_cluster(self, record: object, k):
        raise NotImplementedError

    @abstractmethod
    def make_cluster_unselected(self):
        raise NotImplementedError

    @abstractmethod
    def farthest_from(self, record: object):
        raise NotImplementedError

    @abstractmethod
    def unselected_length(self):
        raise NotImplementedError
