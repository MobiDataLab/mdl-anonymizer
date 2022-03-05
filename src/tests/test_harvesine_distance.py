import timeit

from src.entities.TimestampedLocation import TimestampedLocation

location_orig = TimestampedLocation(1212909273, -122.41131, 37.78724)
location_anon_1 = TimestampedLocation(1212909216, -122.41819763183594, 37.79029083251953)
location_anon_2 = TimestampedLocation(1212909216, -122.41552734375, 37.78963088989258)

# print(location_orig.spatial_distance(location_anon_1))
# print(location_orig.spatial_distance(location_anon_2))

t = timeit.timeit('location_orig.spatial_distance(location_anon_1)',
              setup='from src.entities.TimestampedLocation import TimestampedLocation; location_orig = TimestampedLocation(1212909273, -122.41131, 37.78724); location_anon_1 = TimestampedLocation(1212909216, -122.41819763183594, 37.79029083251953)'
              , number=1000000)
print(t)


t = timeit.timeit('location_orig.temporal_distance(location_anon_1)',
              setup='from src.entities.TimestampedLocation import TimestampedLocation; location_orig = TimestampedLocation(1212909273, -122.41131, 37.78724); location_anon_1 = TimestampedLocation(1212909216, -122.41819763183594, 37.79029083251953)'
              , number=1000000)
print(t)