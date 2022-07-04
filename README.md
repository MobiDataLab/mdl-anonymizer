# MobiDataLab anonymization module
Python module for mobility data anonymization of the [MobiDataLab](https://mobidatalab.eu/) European project.

Developed by [CRISES research group](https://crises-deim.urv.cat/web/) from [URV](https://www.urv.cat/en/).


## Table of Contents
* [Install](#install)
* [Usage](#usage)
  * [CLI](#cli)
    * [Anonymization methods](#anonymization-methods)
    * [Utility metrics](#utility-metrics)
  * [By code](#by-code)

## Install
To install the package, run the commands below in a terminal located at the root of this repository.
This will create a <a href="https://docs.conda.io/projects/conda/en/latest/">Conda</a> environment, install the dependencies and setup the module.
Setup is only required for importing the module into Python code, not for CLI usage (see [Usage section](#usage)).
```bash
# Create and activate environment
conda create --name mda_env -y
conda activate mda_env

# Install dependencies
conda install rtree -y
conda install tqdm -y
conda install -c conda-forge haversine -y
conda install -c conda-forge scikit-mobility -y
conda install typer -y

# [Optional] Build and setup the package for Python import, not required for CLI usage
conda install conda-build
conda develop mob_data_anonymizer
```

Tested to work with the following software versions:
* Python: 3.8 and 3.10
* Conda: 4.11.0
* Operating System: Ubuntu 20.04

## Usage
This module can be employed as a command line interface (CLI) or by Python code.
Following subsections illustrate their usage.

### CLI
The developed package provides a command line interface (CLI) that lets users anonymize a mobility dataset and compute some utility measures over both the original and the anonymized datasets in a straightforward way.
```bash
python -m mob_data_anonymizer
```

#### Anonymization methods
The parameter values to configure the anonymization methods are provided to the application using a JSON file:  
```bash
python -m mob_data_anonymizer anonymize -f parameters_file.json
```
There are some common parameters to all the anonymization methods:
* method (string): The name of the anonymization method to be executed. Must be one of the following:
  * SwapMob
  * Microaggregation
  * SwapLocations
* input_file (string): The dataset to be anonymized
* output_folder (string, optional): Folder to save the generated output datasets
* main_output_file (string. optional): The name of the anonymized dataset 
* save_filtered_dataset (boolean, optional): True: Export the pre-processed dataset
* filtered_file (string, optional): The name of the pre-processed dataset

Each of the anonymization methods has some specific parameters that have to be added to the parameters file:
* SwapMob (configuration file example [here](examples/config_SwapMob.json)):
  * spatial_thold (float): Maximum distance (in km) to consider two locations as close
  * temporal_thold (int): Maximum time difference (in seconds) to consider two locations as coexistent 
  * min_n_swap (int, optional): Minimum number of swaps for a trajectory for not being removed.
  * seed (int, optional): Seed for the random swapping process
* Microaggregation (configuration file example [here](examples/config_Microaggregation.json)):
  * k (int): Minimum number of trajectories to be aggregated in a cluster
* SwapLocations (configuration file example [here](examples/config_SwapLocations.json)):
  * k (int):  Minimum number of locations of the swapping cluster
  * min_r_s (int): Minimum spatial radius of the swapping cluster (in meters)
  * max_r_s (int): Maximum spatial radius for building the swapping cluster (in meters)
  * min_r_t (int): Minimum temporal threshold for building the swapping cluster (in seconds)
  * max_r_t (int): Maximum temporal threshold for building the swapping cluster (in seconds)

#### Utility metrics
As previously mentioned, the anonymization module also includes a tool to compute and compare some utility metrics of original and anonymized datasets. We leverage on the well-known scikit-mobility1 library to compute these utility metrics. To compute some of these measures, the datasets to be compared are previously tessellated.

Again, the parameter values to compute the measures are provided to the application through a JSON file:
```bash
python –m mob_data_anonymizer measures -f parameters_file.json 
```
Available parameters are:
* method (array): The name of the measures to compute. Must be some of the following (please, visit the [scikit-mobility website](https://scikit-mobility.github.io/scikit-mobility/reference/measures.html) for details):
  * visits_per_location
  * distance_straight_line
  * uncorrelated_location_entropy
  * random_location_entropy
  * mean_square_displacement
* mode (string): Type of output. As some measures output is a DataFrame a strategy has to be defined. Must be one of the following:
  * average: computes the average of each DataFrame (from original and anonymized dataset) and send it to stdout
  * export: join and export both output DataFrame (from the original and anonymized datasets) to a single CSV file
* input_1 (string): Filepath of the first dataset 
* input_2 (string): Filepath of the second dataset 
* output_folder (string, optional): Folder to save the generated output files

An example of metrics configurations file can be found [here](examples/config_metrics.json).

### By code
Once the module is installed, its usage only requires from an import:
```python
import mob_data_anonymizer
```
Specific examples are given in the [examples/anonymize/src](examples/anonymize/src) folder.

<!---
## Datasets
- **cabs_dataset_20080608_0700_0715.csv**: 371 trajectories and 3120 locations. All locations between 07:00 and 07:15
- **cabs_dataset_0700_0715.csv**: 7265 trajectories and 60628 locations. All locations between 07:00 and 07:15
--->