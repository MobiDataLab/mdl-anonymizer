# MobiDataLab anonymization module

## CLI Usage
The developed package provides a command line interface (CLI) that allows users anonymize a mobility dataset and compute some utility measures over both the original and the anonymized datasets in a straightforward way.
```
python -m mob_data_anonymizer
```

### Anonymization methods
The parameter values to configure the anonymization methods are provided to the application using a JSON file:  
```
python -m mob_data_anonymizer anonymize -f parameters_file.json
```
There are some common parameters to all the anonymization methods:
* method (string): The name of the anonymization method to be executed. Must be one of those defined in [config.json](../mdl_anonymizer/config.json). Currently, 
they are the following:
  * [SimpleGeneralization](anonymization/SimpleGeneralization.md)
  * [ProtectedGeneralization](anonymization/ProtectedGeneralization.md)
  * [Microaggregation](anonymization/Microaggregation.md)
  * [TimePartMicroaggregation](anonymization/TimepartMicroaggregation.md)
  * [SwapAllLocations](anonymization/SwapAllLocations.md)
  * [SwapMob](anonymization/SwapMob.md)
* input_file (string): The dataset to be anonymized
* output_folder (string, optional): Folder to save the generated output datasets
* main_output_file (string, optional): The name of the anonymized dataset 
* params (JSON object, optional): Specific parameters of the corresponding anonymized method

Please, visit the section related to every method to know their specific parameters and the [examples folder](../examples/configs/) to find some examples of config files.

### Utility and privacy metrics
The anonymization module also includes tools to compute and compare some utility and privacy metrics of original and anonymized datasets. Again, the parameter values to compute the measures are provided to the application through a JSON file.

```
python –m mob_data_anonymizer measures -f parameter_file.json
```

The parameter file contains all the measures to be computed with their corresponding parameters:

- original_dataset (str): Path of the original dataset
- anonymized_dataset (str): Path of the anonymized dataset
- output_folder (string, optional): Folder to save the generated outputs 
- main_output_file (string, optional): Name of the main output file
- measures (Array of JSON objects): List of measures to be computed. Every measure includes their own parameters (if any). They should appear in the main configuration file ([config.json](../mdl_anonymizer/config.json)). Currently, these are the developed measures: 
  - ScikitMeasures
  - [RSME](metrics/rsme.md)
  - [PropensityScore](metrics/propensityScore.md)
  - [RecordLinkage](metrics/recordLinkage.md)
  - TrajectoriesRemoved

Please, visit the [examples folder](../examples/configs/config_measures.json) to find an example of config file to compute some measures.

### Privacy-preserving analysis methods

The parameter values to configure the anonymization methods are provided to the application using a JSON file: 
```
python -m mob_data_anonymizer analysis -f parameters_file.json
```

There are some common parameters to all the analysis methods:
* method (string): The name of the analysis method to be executed. Must be one of those defined in [config.json](../mdl_anonymizer/config.json). Currently, 
they are the following:
  * [QuadTreeHeatMap](analysis/QuadTreeHeatMap.md)
* input_file (string): The dataset to be analyzed
* output_folder (string, optional): Folder to save the ouputs
* main_output_file (string, optional): The name of the main output file
* params (JSON object, optional): Specific parameters of the corresponding analysis method

Please, visit the section related to every method to know their specific parameters and the [examples folder](../examples/configs/) to find some examples of config files.

### Filtering
In addition, the anonymization module also provides some filtering functionality. Again, these functionalities can be extended by developing further filtering methods.

```
python –m mob_data_anonymizer filter -f parameter_file.json
```

In this case, the config file has the following parameters:
- input_filename (str): Filename of the dataset to be filtered 
- output_filename (str, optional): The name of the output file
- methods (array of JSON objects): Name and value of each filtering methods that should be applied to the dataset. Currently just two filtering mechanisms are implemented:
  - min_locations: Remove trajectories with less that {value} locations
  -	max_speed: Remove trajectories with a speed greater than {value} between two of its locations.

Please, visit the [examples folder](../examples/configs/config_filter.json) to find an example of config file 
for filtering a dataset.