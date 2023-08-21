# Tests

from load.aphrodite import collect_APHRO
import xarray as xr
import numpy as np
import pandas as pd

# test inputs
minyear = 1970
maxyear = 1971
location = 'indus'

# TODO generalise tests for all dataset functions


def test_collect_is_dataset():
    """ Check if dataset is a valid format"""
    dataset = collect_APHRO(location='indus', minyear=minyear, maxyear=maxyear)
    assert isinstance(dataset, xr.DataSet), "dataset is not an xarray Dataset"


def test_collect_has_lon():
    """ Check if dataset has 'lon' variable."""
    dataset = collect_APHRO(location='indus', minyear=minyear, maxyear=maxyear)
    headers = list(dataset.dims)
    if 'lon' not in headers:
        if 'longitude' in headers:
            assert 'lon' in headers, "change 'longitude' header to 'lon'"
        else:
            assert 'lon' in headers, "no 'lon'"


def test_collect_has_lat():
    """ Check if dataset has 'lat' variable."""
    dataset = collect_APHRO(
        location='indus', minyear=minyear, maxyear=maxyear)
    headers = list(dataset.dims)
    if 'lat' not in headers:
        if 'latitude' in headers:
            assert 'lat' in headers, "change 'latitude' header to 'lat'"
        else:
            assert 'lon' in headers, "no 'lon'"


def test_collect_has_time():
    """Check if dataset has 'time' variable."""
    dataset = collect_APHRO(
        location='indus', minyear=minyear, maxyear=maxyear)
    headers = list(dataset.dims)
    if 'time' not in headers:
        if 'date' in headers:
            assert 'time' in headers, "change 'date' header to 'time'"
        else:
            assert 'time' in headers, "no 'time'"


def test_collect_is_datetime():
    """Check if 'time' is datetime64."""

    dataset = collect_APHRO(
        location='indus', minyear=minyear, maxyear=maxyear)
    assert dataset.time.dtype is np.datetime64, "time is not datetime64"

    assert np.issubdtype(dataset.time.dtype, np.datetime64)

    dataset_df = dataset.time.to_dataframe()
    dataset_df.set_index('time', inplace=True)
    assert all(dataset_df.index.is_month_start ==
               True), "time is not month start"
