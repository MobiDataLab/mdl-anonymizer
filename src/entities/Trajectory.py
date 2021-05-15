from src.entities.TimestampedLocation import TimestampedLocation


class Trajectory:
    def __init__(self, id):
        self.id = id
        self.locations = []

    def add_location(self, location: TimestampedLocation):
        if len(self.locations) > 0 and location.timestamp <= self.last_timestamp():
            # Keep the list of trajectories sorted
            self.locations.append(location)
            self.locations.sort(key=lambda x: x.timestamp)
        else:
            self.locations.append(location)

    def add_locations(self, locations: list):
        locations.sort(key=lambda l: l.timestamp)
        self.locations.extend(locations)

    def first_timestamp(self):
        return self.locations[0].timestamp

    def last_timestamp(self):
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

    def get_previous_location_by_timestamp(self, ts):
        prev_loc = None
        for idx, loc in enumerate(self.locations):
            if loc.timestamp >= ts:
                return self.locations[idx-1]

        return None

    def get_next_location_by_timestamp(self, ts):
        for loc in self.locations:
            if loc.timestamp > ts:
                return loc

        return None

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
