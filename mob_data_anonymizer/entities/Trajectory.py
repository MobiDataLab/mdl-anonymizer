from more_itertools import pairwise
from math import sqrt

from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation


class Trajectory:
    def __init__(self, id, user_id=None):
        self.id = id
        self.str_id = str(self.id)
        self.user_id = user_id
        self.index = 0
        self.locations = []
        self.distance_to_reference_trajectory = 0

    def add_location(self, location: TimestampedLocation, sort=True):
        self.locations.append(location)
        if sort:
            self.locations.sort(key=lambda x: x.timestamp)

    def add_locations(self, locations: list):
        locations.sort(key=lambda l: l.timestamp)
        self.locations.extend(locations)

    def get_first_timestamp(self):
        return self.locations[0].timestamp

    def get_last_timestamp(self):
        return self.locations[-1].timestamp

    def get_timestamps(self):
        return [l.timestamp for l in self.locations]

    def get_interval_timestamps(self, interval: tuple):
        return [l.timestamp for l in self.locations if interval[0] <= l.timestamp <= interval[1]]

    def get_location_by_timestamp(self, ts):
        for loc in self.locations:
            if loc.timestamp == ts:
                return loc

        return None

    def filter_by_interval(self, interval: tuple):
        return [l for l in self.locations if interval[0] <= l.timestamp <= interval[1]]

    def get_previous_location_by_timestamp(self, ts):
        prev_loc = None
        for idx, loc in enumerate(self.locations):
            if loc.timestamp >= ts:
                return self.locations[idx - 1]

        return None

    def get_next_location_by_timestamp(self, ts):
        for loc in self.locations:
            if loc.timestamp > ts:
                return loc

        return None

    def get_length(self, unit='km'):
        def distance(pair):
            return pair[0].spatial_distance(pair[1])

        pairs = pairwise(self.locations)

        length = sum(map(distance, pairs))

        return length

    def get_avg_speed(self, unit='kmh', sp_type='Haversine') -> float:

        avg_speed = 0.0
        for i, l1 in enumerate(self.locations):
            try:
                l2 = self.locations[i + 1]
                avg_speed += (l1.spatial_distance(l2, sp_type) / l1.temporal_distance(l2))
            except IndexError:
                if len(self.locations) == 1:
                    avg_speed += 0
                else:
                    avg_speed /= (len(self.locations) - 1)
            except ZeroDivisionError:
                avg_speed += 0

        # Return km/h
        if unit == 'kmh':
            return avg_speed * 3600
        else:
            return avg_speed

    def some_speed_over(self, max_speed_kmh) -> bool:
        '''

        :param max_speed: kmh
        :return: bool
        '''
        for i, l1 in enumerate(self.locations):
            try:
                l2 = self.locations[i + 1]
                if l1.temporal_distance(l2) == 0:
                    return True
                speed = (l1.spatial_distance(l2) / l1.temporal_distance(l2)) * 3600
                if speed > max_speed_kmh:
                    return True
            except IndexError:
                return False

    def some_location_outside(self, bbox: tuple) -> bool:
        '''
        bbox (min_lng, min_lat, max_lng, max_lat)
        '''

        min_lng, min_lat, max_lng, max_lat = bbox

        for l in self.locations:
            if not min_lng <= l.x <= max_lng:
                return True
            if not min_lat <= l.y <= max_lat:
                return True

        return False

    def default_distance(self, trajectory, p_lambda) -> float:
        avg_speed_1 = self.get_avg_speed(sp_type="Haversine")
        avg_speed_2 = trajectory.get_avg_speed(sp_type="Haversine")
        avg_speed = (avg_speed_1 + avg_speed_2) / 2
        avg_speed /= 3.6  # m/s

        h = round((len(self) + len(trajectory)) / 2)
        gap_1 = len(self) / h
        gap_2 = len(trajectory) / h

        index_1 = index_2 = 0
        i = j = 0

        d = 0

        for k in range(h):

            if i == len(self):
                i = len(self) - 1

            if j == len(trajectory):
                j = len(trajectory) - 1

            loc_1 = self.locations[i]
            loc_2 = trajectory.locations[j]

            d1 = loc_1.spatial_distance(loc_2, type="Haversine") * 1000  # meters
            d2 = p_lambda * (loc_1.temporal_distance(loc_2)) * avg_speed  # meters
            d += pow(d1 + d2, 2)

            index_1 += gap_1
            index_2 += gap_2

            i = round(index_1)
            j = round(index_2)

        d /= h

        d = sqrt(d)

        return d

    def __len__(self):
        return len(self.locations)

    def __str__(self):
        string = f"T {self.id} ({len(self.locations)} locations): "
        for loc in self.locations[:5]:
            string += f'[{loc.timestamp}: {loc.x}, {loc.y}] '

        if len(self.locations) > 5:
            string += "..."

        return string

    def __hash__(self):
        string = ""
        for loc in self.locations:
            string += f'[{loc.timestamp}: {loc.x}, {loc.y}] '

        return hash(string)

    def __eq__(self, other):
        return hash(hash(self) == hash(other))

    def __repr__(self):
        return str(self)
