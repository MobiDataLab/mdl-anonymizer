from math import sqrt


class TimestampedLocation:
    def __init__(self, timestamp, x, y):
        self.timestamp = int(timestamp)
        self.x = float(x)
        self.y = float(y)

    def get_list(self):
        return [self.timestamp, self.x, self.y]

    def __str__(self):
        return f'[{self.timestamp}: {self.x}, {self.y}]'

    def __eq__(self, other):
        if not isinstance(other, TimestampedLocation):
            return NotImplemented

        return self.timestamp == other.timestamp and self.x == other.x and self.y == other.y

    def distance(self, location):
        return sqrt((location.x - self.x) ** 2 + (location.y - self.y) ** 2 + (location.timestamp - self.timestamp) ** 2)

    @staticmethod
    def compute_centroid(locations: list):
        x = 0
        y = 0
        ts = 0
        for l in locations:
            x += l.x
            y += l.y
            ts += l.timestamp

        x /= len(locations)
        y /= len(locations)
        ts /= len(locations)

        return TimestampedLocation(round(ts, 2), round(x, 2), round(y, 2))





