# Microaggregation
Even though k-anonymity has usually been enforced via generalization of values, this entails a large information loss 
for high-dimensional and spread data such trajectories. A more utility-preserving alternative to generalization is 
microaggregation [^1]. Trajectory microaggregation is based on partitioning the data set into disjoint clusters 
containing each at least k similar trajectories. Once the clustering of the data set is complete, the trajectories 
in each cluster are aggregated by replacing them with the cluster centroid. During the clustering stage, trajectories 
are grouped minimizing their intra-cluster distance. In the aggregation step, the centroid of the 
data set is calculated as the trajectory in the data set that minimizes the distance to the rest of trajectories. 
In this manner, the resulting microaggregated data set minimizes the information loss incurred when 
enforcing k-anonymity.

## Specific parameters

- k (int, optional, default: 3): Minimum number of trajectories to be aggregated in a cluster
- clustering_method (JSON object, optional, default: SimpleMDAV): Name and parameters (if any) of the method to cluster the trajectories. Must be one of those defined in [config.json](../../mob_data_anonymizer/config.json)
- aggregation_method (JSON object, optional, default: Mean_trajectory): Name and parameters (if any) of the method to aggregate the trajectories within a cluster. Must be one of those defined in [config.json](../../mob_data_anonymizer/config.json)

Please, visit the [examples folder](../../examples/configs/config_Microaggregation.json) to find an example of config file 
for the Microaggregation method.

[^1]: J. Domingo-Ferrer, S. Martínez and David Sánchez, "Decentralized k-anonymization of trajectories via privacy-preserving tit-for-tat", 
Computer Communications, Vol. 190, pp. 57-68, Jun 2022, ISSN: 0140-3664.