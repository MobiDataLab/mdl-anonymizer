# SwapAllLocations
This method is based on the ReachLocation mechanism proposed by [^1]. 
Protection is achieved by permuting the locations in trajectories among 
other trajectories. The method works as follows: first, a cluster is 
created around a randomly selected location based on some spatial and 
temporal threshold parameters provided by the user. If the cluster does 
not include at least k locations from at least k different trajectories, 
the thresholds are increased until we obtain the required number of 
locations or the thresholds reach user-defined maximum values. If a 
valid cluster is built, the locations are swapped among the k 
trajectories (by changing their trajectory IDs) and marked as swapped. 
If no valid cluster can be found around a location, it is removed. 
This process continues until no more “unswapped” locations appear in the 
data set.

This method provides great utility since locations in the resulting 
anonymized trajectories are true, fully accurate original locations. 
No fake, generalized or perturbed locations are given in the anonymized 
data set of trajectories. Besides that, the flow and directions of the 
original trajectories are well-preserved. However, this mechanism does 
not offer a formal guaranty of privacy. If a whole trajectory is unique, 
the user could be identified. 

To mitigate this problem, we have developed a simple trajectory anonymization mechanism like that 
described [here](ProtectedGeneralization.md). After swapping all the locations in the dataset, we build a square grid and 
convert each trajectory into a sequence of tiles. We then analyse the generated sequences to find combinations of 
2 consecutive tiles that occur less than KL times in the anonymized dataset. If such a combination is found, 
the locations within one of the tiles are removed.

## Specific parameters

- k (int, optional, default: 3):  Minimum number of locations of the swapping cluster
- min_r_s (int, optional, default: 100): Minimum spatial radius of the swapping cluster (in meters)
- max_r_s (int, optional, default: 500): Maximum spatial radius for building the swapping cluster (in meters)
- min_r_t (int, optional, default: 60): Minimum temporal threshold for building the swapping cluster (in seconds)
- max_r_t (int, optional, default: 120): Maximum temporal threshold for building the swapping cluster (in seconds)
- tile_size (int, optional, default: 1000): Size of tessellation to improve privacy at trajectory level (in meters)
- seed (int, optional, default: None): Seed for the random swapping process

Please, visit the [examples folder](examples/configs/config_SwapAllLocations.json) to find an example of config file for the SwapAllLocations method.

[^1]: J. Domingo-Ferrer and R. Trujillo-Rasua, "Microaggregation- and permutation-based anonymization of movement 
data", Information Sciences, Vol. 208, pp. 55-80, Nov 2012, ISSN: 0020-0255.