from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation

import unittest


class MyTestCase(unittest.TestCase):
    def test_spatial_distance(self):

        t1 = TimestampedLocation(1213084687, 45.7597, 4.8422)
        t2 = TimestampedLocation(1213084659, 48.8567, 2.3508)

        spatial_distance = t1.spatial_distance(t2)

        self.assertEqual(392.21726, round(spatial_distance, 5))

        t1 = TimestampedLocation(1213084687, 41.3825, 2.1769)  # Barcelona
        t2 = TimestampedLocation(1213084659, 37.3828, -5.9731)  # Sevilla

        spatial_distance = t1.spatial_distance(t2)

        self.assertEqual(829.15804, round(spatial_distance, 5))

    def test_temporal_distance(self):

        t1 = TimestampedLocation(1213084687, 45.7597, 4.8422)
        t2 = TimestampedLocation(1213084659, 48.8567, 2.3508)

        temp_distance = t1.temporal_distance(t2)

        self.assertEqual(28, temp_distance)

if __name__ == '__main__':
    unittest.main()
