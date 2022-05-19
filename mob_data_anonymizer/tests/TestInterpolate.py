import unittest

from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mob_data_anonymizer.utils.Interpolation import interpolate


class TestInterpolate(unittest.TestCase):

    def test_interpolate(self):
        loc_1 = TimestampedLocation(1213083855, 37.79728, -122.39609)
        loc_2 = TimestampedLocation(1213086000, 37.79838, -122.40239)
        point = interpolate(loc_1, loc_2, 1213085090)
        # self.assertEqual(point, (5, 40))
        print(point)

if __name__ == '__main__':
    unittest.main()
