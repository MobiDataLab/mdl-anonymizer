import unittest

from mdl_anonymizer.entities.TimestampedLocation import TimestampedLocation
from mdl_anonymizer.entities.Trajectory import Trajectory


class MyTestCase(unittest.TestCase):
    def test_avg_speed(self):

        traj_1 = Trajectory(1)

        traj_1.add_location(TimestampedLocation(0, 45.7597, 4.8422))
        traj_1.add_location(TimestampedLocation(3600, 48.8567, 2.3508))

        avg_speed = traj_1.get_avg_speed()

        self.assertEqual(392.21726, round(avg_speed, 5))

        traj_1.add_location(TimestampedLocation(7200, 45.7597, 4.8422))
        avg_speed = traj_1.get_avg_speed()

        self.assertEqual(392.21726, round(avg_speed, 5))

        traj_1.add_location(TimestampedLocation(10800, 41.3825, 2.1769))
        avg_speed = traj_1.get_avg_speed()

        self.assertEqual(438.77853, round(avg_speed, 5))

        b = traj_1.some_speed_over(max_speed=300)

        self.assertEqual(True, b)

        traj_2 = Trajectory(2)

        traj_2.add_location(TimestampedLocation(0, 45.7597, 4.8422))
        traj_2.add_location(TimestampedLocation(3600, 45.7534, 4.8434))

        avg_speed = traj_2.get_avg_speed()

        self.assertEqual(0.70669, round(avg_speed, 5))

        b = traj_2.some_speed_over(max_speed=300)

        self.assertEqual(False, b)

if __name__ == '__main__':
    unittest.main()
