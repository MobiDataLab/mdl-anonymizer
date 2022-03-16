# MobiDataLab anonymization module

## Install

Checkout 'master'.

### Option 1

Create conda environment in the PyCharm terminal using the provided yaml file:

`conda env create --name myenv -f environment.yml`

### Option 2

Crear conda interpreter en Pycharm con python 3.8 (no he probado con 3.9 ni 3.10)

Después, en el terminal: 

`conda activate <env>`

`conda install rtree`

`conda install -c conda-forge scikit-mobility` (tarda)

`conda install -c conda-forge haversine`

`conda install networkx`

## Datasets
- **cabs_dataset_20080608_0700_0715.csv**: 371 trajectories and 3120 locations. All locations between 07:00 and 07:15
- **cabs_dataset_0700_0715.csv**: 7265 trajectories and 60628 locations. All locations between 07:00 and 07:15