<p align="center" width="100%">
    <img width="15%" src="figures/load_logo.png">
</p>

# load

Python library for importing and compatibly formatting data from various sources used during my PhD.

## Description

Datasets should all have the same format so they can be easily used together.

In particular, they should be exported from the submodule:

- as a xarray Dataset or pandas Dataframe
- with 'lon' as the longitude variable name in °E (float)
- with 'lat' as the latitude variable name in °N (float)
- with 'time' for time variable name as datetimes. For datasets with monthly resolution, the date should be set to the begining of the month
- with 'tp' for the variable name for total precipitation in mm/day (float)

## Installation

After cloning this repository and navigating to its install directory, the dependencies can be installed with anaconda: `conda env create -f environment.yml` This will create a new anaconda environment 'load'. After activating the environment: `conda activate load`.

Add your data and code directories to the `__init__.py` file.
