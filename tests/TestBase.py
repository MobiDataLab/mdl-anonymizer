import unittest
import warnings
from functools import partialmethod
from tqdm import tqdm

class TestBase(unittest.TestCase):
    def setUp(self):
        # Silence tqdm and warnings
        tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
        warnings.filterwarnings("ignore")

