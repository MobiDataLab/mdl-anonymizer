from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation


class CabLocation(TimestampedLocation):

    def __init__(self, timestamp, x, y, occupancy: bool = True):
        self.occupancy = occupancy
        super().__init__(timestamp, x, y)