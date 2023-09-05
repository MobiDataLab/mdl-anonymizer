# MobiDataLab anonymization module
Python module for mobility data anonymization of the [MobiDataLab](https://mobidatalab.eu/) European project.

Developed by [CRISES research group](https://crises-deim.urv.cat/web/) from [URV](https://www.urv.cat/en/).


## Table of Contents
- [Install](#install)
- [Usage](#usage)
  - [CLI](#cli)
  - [API](#api)
  - [As a library](#as-a-library)
- [Contributing](#contributing)

## Install
To install the package, run the commands below in a terminal located at the root of this repository.
This will create a <a href="https://docs.conda.io/projects/conda/en/latest/">Conda</a> environment, install the dependencies and setup the module.
Setup is only required when using the module as a library in Python code, not for CLI usage (see [Usage section](#usage)).
```bash

# Create and activate environment
conda create -n mdl_env pip python=3.9 rtree
conda activate mda_env

# Install dependencies
conda install -c conda-forge scikit-mobility -y   # If this fails, use "pip install scikit-mobility"
conda install -c conda-forge pyarrow -y
conda install -c conda-forge py-xgboost
conda install -c conda-forge haversine -y
conda install tqdm typer more-itertools -y

# [Optional] API
conda install -c conda-forge fastapi
conda install -c conda-forge uvicorn
conda install -c conda-forge python-multipart


# [Optional] Build and setup the package for Python import, not required for CLI usage
conda install conda-build
conda develop mob_data_anonymizer
```

Tested to work with the following software versions:
* Python: 3.9 and 3.10
* Conda: 4.11.0 and 4.12.0
* Operating System: Ubuntu 20.04 and Windows 10

## Usage
This module can be used as an independent command line interface (CLI) tool or as a Python library.
Following subsections illustrate their usage.

### CLI
The developed package provides a command line interface (CLI) that allows users anonymizing a mobility dataset, performing an analysis in a private-way and compute some utility and privacy measures measures over both the original and the anonymized datasets in a straightforward way.
```
python -m mob_data_anonymizer
```
You can find a detailed documentation [here](docs/README.md).

### API

The anonymization module is also ready to be deployed in a server to provide all its functionality remotely.
To start the server application, use the following command:

```
uvicorn mob_data_anonymizer.server.main_api:app --reload --host 0.0.0.0 --port 8000
```

See a detailed documentation [here](docs/API.md)

### As a library
Once the module is installed, its usage only requires an import:
```python
import mob_data_anonymizer
```
You can find examples of how to use the library in the [examples folder](examples).

## Contributing
The anonymization module has been designed with a focus on modularity, where pseudonymization or anonymization methods can be built using different components dedicated to preprocessing, clustering, distance computation, aggregation, etc. We have focused on making it easy to add new methods and components, in order to encourage contributions from other researchers.

To do so, developers should simply follow the next steps:
1. Create a Python class that implements (inherits from), respectively:
   1.	*AnonymizationMethodInterface*, for new anonymization methods
   2.	*TrajectoryAggregationInterface*, for new aggregation methods
   3.	*AnalysisMethodInterface*, for new analysis methods
   4.	*ClusteringInterface*, for new clustering methods
   5.	*MeasuresMethodInterface*, for new measure methods
   6.	*DistanceInterface*, for new trajectory distance methods
2. The constructor of the new class must receive as arguments first the original dataset and then the necessary parameters for the new method.
3. Implement the inherited class method `run()` by including the code that executes the logic of the new method (e.g., in the case of a new anonymization method, the routine that anonymizes the original dataset)
4. Include the reference description to the new class method in the main configuration file ([config.json](mob_data_anonymizer/config.json)) archive located at the root of the project library. The reference must be included inside the method type (anonymization, clustering, aggregation, trajectory_distances, analysis, or measures) and it must contain the name of the method and the path name of the new class.
5. Add a Unit Test to the [test folder](tests). We recommend to use a [mock dataset](examples/data/mock_dataset.csv) included in the [data folder](examples/data).
6. Don't forget to add a description of your method in the [docs section](docs).

Once the new method has been implemented and referenced in the [config.json](mob_data_anonymizer/config.json) file as described above, the new method can be used in the same way as those already developed.  

