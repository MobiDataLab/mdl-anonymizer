# Time Partitioned Microaggregation 
[Microaggregation](Microaggregation.md) is a utility-preserving method to enforce k-anonymity in high-dimensional 
and spread data such trajectories. The partition and aggregation steps produce some information loss. The goal of 
microaggregation is to minimize the information loss according to some utility metric. For this reason, microaggregation 
is considered a good approach to anonymize trajectories when the utility of original data should be preserved as much 
as possible. On the other hand, the runtime of the microaggregation algorithm can be unfeasible for large datasets and 
small k values. This is because the computational cost of the microaggregation algorithm scales  O(n^2⁄k), 
here n is the number of trajectories in the dataset and k is the minimum number of trajectories sharing the same 
combination (that is, the desired level of privacy).

To solve this issue in large datasets, we have based on microaggregation to propose the method Time Partitioned Microaggregation of trajectories (TimePartMicroaggregation) with the following features:
- Since the runtime lowers as n decreases, we propose to first partition the original dataset into smaller datasets based on the time dimension of the trajectories.
- Each partition contains the trajectories in a given time interval. In this way, the trajectories contained in the resulting small datasets are similar in time and can be clustered based only on their spatial distance.
- This method results in a feasible runtime for large datasets at the cost of a higher (but assumable) information loss compared to the microaggregation method. This is because the microaggregation method searches for similar trajectories through the entire dataset to group clusters while the TimePartMicroaggregation method searches only in the smaller partitions of the dataset.


## Specific parameters

- k (int, optional, default: 3): Minimum number of trajectories to be aggregated in a cluster
- interval (int, optional, default: 900): Time interval in each partitioned dataset (in seconds)
- clustering_method (JSON object, optional, default: SimpleMDAV): Name and parameters (if any) of the method to cluster the trajectories. Must be one of those defined in [config.json](../../mob_data_anonymizer/config.json)
- aggregation_method (JSON object, optional, default: Mean_trajectory): Name and parameters (if any) of the method to aggregate the trajectories within a cluster. Must be one of those defined in [config.json](../../mob_data_anonymizer/config.json)

Please, visit the [examples folder](../../examples/configs/config_TimePartMicroaggregation.json) to find an example of config file 
for the Time PartitionMicroaggregation method.