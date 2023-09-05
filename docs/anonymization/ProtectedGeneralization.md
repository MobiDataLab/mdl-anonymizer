# Protected Generalization
An attacker with access to the anonymized trajectory dataset may know: 1) the details of the schema used to anonymize 
the data; 2) the fact that a given user U is in the dataset; and 3) a number KL of locations relative to U and the time
at which they were visited (with a certain precision). With this information, the attacker could try to infer the 
anonymized locations corresponding to the known ones and identify the entire trajectory relative to U.

k-Anonymity limits the capability of an attacker who knows a set of features on a subject (some locations and/or 
timestamps in the case of trajectory data) to successfully re-identify individuals in a released dataset. A trajectory 
dataset satisfies k-anonymity if, for each combination of locations and/or timestamps, at least k trajectories share 
the same combination. Thus, the probability of correct re-identification is at most 1/k.

The ProtectedGeneralization method aims to build a k-anonymous version of the original dataset by means of generalization and supression. 

If a custom tessellation is not provided, the first step of the ProtectedGeneralization method is to generate a square tessellation of the geographical area covered by the trajectories in the dataset. A user can define the size of each tile in the tessellation by specifying the parameter tile_size. The larger the size of every tile is, the more trajectories and locations will be preserved in the anonymized dataset, but with less precision. The user can also protect the time dimension, by defining a time_interval. A kind of 3D tessellation is built, with a spatial tessellation defined for every time level containing the locations with timestamps between the defined bounds.

If a custom tessellation is not provided, after building it and mapping all the locations to the corresponding tiles, we perform an optimization preprocessing by merging some tiles in the same time level with a number of locations lower than 3k (see Figure 12). This improves the probability of preserving combinations. Each trajectory is then transformed into a sequence of visits to the resulting tiles.

Now we can generate a generalized version of the dataset X. However, to complete the anonymization procedure, we need to ensure that X’ is a k-anonymous version of X. Firstly, we compute all existing combinations of size KL and count the occurrences of each combination. KL is also a parameter defined by the user and represents the number of locations that an attacker could know from a user U. A larger KL, more locations removed from the original dataset.

Next, we identify and break the ‘bad combinations’ (those whose appear less than k times) by removing some tiles from the trajectory sequences. For each trajectory sequence, we remove the tiles appearing in the ‘bad combinations’, starting from the most to the least common. In case of tie, we check the tiles appearing the ‘good combinations’ to decide which tile remove first.

After processing all the trajectory sequences, we have broken all the ‘bad combinations’, but we might have created new ones. Therefore, we compute all existing combinations of size KL again and count the occurrences of each combination. If we find any new ‘bad combinations’, we repeat the removal process until no new ‘bad combinations’ are generated.

Finally, the last step is to create the anonymized dataset X’ from the remaining trajectory sequences. To do so, a user can choose between computing the average of the locations within each tile (which improves utility) or taking the centroid of the tile as the generalized location, using the parameter strategy. Parameter time_strategy allows the user to decide whether to preserve the original timestamps or to take the same timestamp for every tile (improving privacy but harming utility). The decision should consider the time_interval parameter and the precision of the attacker’s knowledge regarding the time when the known locations were visited. For example, if we assume that an attacker only knows the date and the hour (but not the exact minute) when a location was visited, we can define a 60-minute time interval and preserve the original timestamps because all the locations in the same tile share the same hour and are indistinguishable to the attacker. On the other hand, if the user wants to protect the dataset assuming that an attacker knows the accurate timestamp of a specific location, we should use the same timestamp for all the locations, which will improve privacy but reduce the utility of the dataset.



## Specific parameters

- tiles_filename (str, optional, default: None): Tiles files for tessellation (geojson or shapefile)
- tile_size (int, optional, default: 500): If a tiles file is not provided, a squared tessellation of size ‘tile_size’ is generated (in meters)
- time_interval (int, optional, default: None): Size of every time level (in minutes)

Please, visit the [examples folder](../../examples/configs/config_ProtectedGeneralization.json) to find an example of config file 
for the Protected Generalization method.