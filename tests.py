# Tests

from load import aphrodite, era5, cordex
import xarray as xr
import numpy as np
import pandas as pd
import pytest

# test inputs
minyear = '1996'
maxyear = '1998'
location = 'indus'

# TODO generalise tests for all dataset functions

function_list = [aphrodite.collect_APHRO,
                 era5.collect_ERA5]


@pytest.mark.parametrize("collect_function", function_list)
def test_collect_is_dataset(collect_function):
    """ Check if dataset is a valid format"""
    dataset = collect_function(
        location=location, minyear=minyear, maxyear=maxyear)
    assert isinstance(dataset, xr.Dataset), "dataset is not an xarray Dataset"


@pytest.mark.parametrize("collect_function", function_list)
def test_collect_has_tp(collect_function):
    """ Check if dataset has 'tp' variable."""
    dataset = collect_function(
        location=location, minyear=minyear, maxyear=maxyear)
    vars = list(dataset)
    if 'tp' not in vars:
        if 'precipitation' in vars:
            assert 'tp' in vars, "change 'precipiation' dim 'tp'"
        else:
            assert 'tp' in vars, "no 'tp' dim"


@pytest.mark.parametrize("collect_function", function_list)
def test_collect_has_lon(collect_function):
    """ Check if dataset has 'lon' variable."""
    dataset = collect_function(
        location=location, minyear=minyear, maxyear=maxyear)
    dims = list(dataset.dims)
    if 'lon' not in dims:
        if 'longitude' in dims:
            assert 'lon' in dims, "change 'longitude' dim 'lon'"
        else:
            assert 'lon' in dims, "no 'lon' dim"


@pytest.mark.parametrize("collect_function", function_list)
def test_collect_has_lat(collect_function):
    """ Check if dataset has 'lat' variable."""
    dataset = collect_function(
        location=location, minyear=minyear, maxyear=maxyear)
    dims = list(dataset.dims)
    if 'lat' not in dims:
        if 'latitude' in dims:
            assert 'lat' in dims, "change 'latitude' dim 'lat'"
        else:
            assert 'lon' in dims, "no 'lon' dim"


@pytest.mark.parametrize("collect_function", function_list)
def test_collect_has_time(collect_function):
    """Check if dataset has 'time' variable."""
    dataset = collect_function(
        location=location, minyear=minyear, maxyear=maxyear)
    dims = list(dataset.dims)
    if 'time' not in dims:
        if 'date' in dims:
            assert 'time' in dims, "change 'date' dim 'time'"
        else:
            assert 'time' in dims, "no 'time dim'"


@pytest.mark.parametrize("collect_function", function_list)
def test_collect_is_datetime(collect_function):
    """Check if 'time' is datetime64."""

    dataset = collect_function(
        location=location, minyear=minyear, maxyear=maxyear)

    assert np.issubdtype(dataset.time.dtype,
                         np.datetime64),  "time is not datetime64"

    dataset_df = dataset.time.to_dataframe()
    dataset_df.set_index('time', inplace=True)
    assert all(dataset_df.index.is_month_start ==
               True), "time is not month start"
