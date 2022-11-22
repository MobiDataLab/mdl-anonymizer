from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation


class Trajectory:
    def __init__(self, id, user_id=None):
        self.id = id
        self.user_id = user_id
        self.index = 0
        self.locations = []

    def add_location(self, location: TimestampedLocation):
        if len(self.locations) > 0 and location.timestamp <= self.get_last_timestamp():
            # Keep the list of trajectories sorted
            self.locations.append(location)
            self.locations.sort(key=lambda x: x.timestamp)
        else:
            self.locations.append(location)

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

    def get_avg_speed(self, unit='kmh', sp_type='Haversine') -> float:

        avg_speed = 0.0
        for i, l1 in enumerate(self.locations):
            try:
                l2 = self.locations[i + 1]
                avg_speed += (l1.spatial_distance(l2, sp_type) / l1.temporal_distance(l2))
            except IndexError:
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
                speed = (l1.spatial_distance(l2) / l1.temporal_distance(l2)) * 3600
                if speed > max_speed_kmh:
                    return True
            except IndexError:
                return False

    def __len__(self):
        return len(self.locations)

    def __str__(self):
        string = f"T {self.id} ({len(self.locations)} locations): "
        for loc in self.locations[:5]:
            string += f'[{loc.timestamp}: {loc.x}, {loc.y}] '

        if len(self.locations) > 5:
            string += "..."

        return string

    def __repr__(self):
        return str(self)
