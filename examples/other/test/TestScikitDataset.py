import unittest

from examples.anonymize.src.entities.CabDatasetTXT import CabDatasetTXT


class MyTestCase(unittest.TestCase):
    def test_something(self):
        dataset = CabDatasetTXT()
        dataset.load_from_scikit('cabs_scikit.csv', datetime_key="timestamp")

        print(len(dataset.trajectories))
        print(dataset.get_number_of_locations())

        dataset.export_to_scikit()



if __name__ == '__main__':
    unittest.main()
