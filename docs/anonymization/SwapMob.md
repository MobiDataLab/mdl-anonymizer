# SwapMob
SwapMob, proposed by J. Salas, D. Megías and V. Torra [^1]
is a perturbative anonymization method based on swapping 
segments of trajectories with other trajectories. When two locations in two different trajectories 
are close enough (when they cross each other), according to some threshold of proximity and time set by the user, 
the two remaining subtrajectories are swapped between the two original trajectories (that is, the ID of 
the previous locations of each trajectory are swapped). Changing pseudonyms (IDs) is equivalent to swapping the 
partial trajectories. If a trajectory does not cross any other one, and therefore, no subtrajectory is swapped with 
other trajectories, it is removed. 

Hence, the relation between data subjects and their data is obfuscated while keeping a precise aggregated data, 
such as the number of users and their directions on any given zone at a specific time, 
the locations that have been visited by different anonymous users or the average length of trajectories.

Nevertheless, this comes at the cost of modifying the trajectories and losing individual trajectory mining utility.

## Specific parameters

- spatial_thold (float): Maximum distance (in km) to consider two locations as close
- temporal_thold (int): Maximum time difference (in seconds) to consider two locations as coexistent 
- min_n_swap (int, optional): Minimum number of swaps for a trajectory for not being removed.
- seed (int, optional): Seed for the random swapping process

Please, visit the [examples folder](examples/configs/config_SwapMob.json) to find an example of config file for the SwapMob method.

[^1]: 4.	J. Salas, D. Megías and V. Torra, “SwapMob: Swapping Trajectories for Mobility Anonymization”. 
Privacy in Statistical Databases – PSD2018. Lecture Notes in Computer Science vol. 11126, pp. 331-346. Sep 2018.