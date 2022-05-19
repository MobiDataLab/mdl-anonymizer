from mob_data_anonymizer.entities.TimestampedLocation import TimestampedLocation


def interpolate(loc_1: TimestampedLocation, loc_2: TimestampedLocation, new_timestamp):
    t = (new_timestamp - loc_1.timestamp) / (loc_2.timestamp - loc_1.timestamp)
    point_1 = (loc_1.x, loc_1.y)
    point_2 = (loc_2.x, loc_2.y)
    ret = tuple((1 - t) * coor_1 + t * coor_2 for coor_1, coor_2 in zip(point_1, point_2))
    return ret
