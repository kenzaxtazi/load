# Tests for 'collect' functions

from load.aphrodite import collect_APHRO
import xarray as xr
import numpy as np
import pandas as pd

minyear = 1970
maxyear = 1971
location = 'indus'


def test_collect_is_dataset():
    dataset = collect_APHRO(location='indus', minyear=minyear, maxyear=maxyear)
    assert isinstance(dataset, xr.DataSet), "dataset is not an xarray Dataset"


def test_collect_has_lon():
    dataset = collect_APHRO(location='indus', minyear=minyear, maxyear=maxyear)
    headers = list(dataset.dims)
    if 'lon' not in headers:
        if 'longitude' in headers:
            assert 'lon' in headers, "change 'longitude' header to 'lon'"
        else:
            assert 'lon' in headers, "no 'lon'"


def test_collect_has_lat():
    dataset = collect_APHRO(
        location='indus', minyear=minyear, maxyear=maxyear)
    headers = list(dataset.dims)
    if 'lat' not in headers:
        if 'latitude' in headers:
            assert 'lat' in headers, "change 'latitude' header to 'lat'"
        else:
            assert 'lon' in headers, "no 'lon'"


def test_collect_has_time():
    dataset = collect_APHRO(
        location='indus', minyear=minyear, maxyear=maxyear)
    headers = list(dataset.dims)
    if 'time' not in headers:
        if 'date' in headers:
            assert 'time' in headers, "change 'date' header to 'time'"
        else:
            assert 'time' in headers, "no 'time'"


def test_collect_is_datetime():

    dataset = collect_APHRO(
        location='indus', minyear=minyear, maxyear=maxyear)
    assert dataset.time.dtype is np.datetime64, "time is not datetime64"

    assert np.issubdtype(dataset.time.dtype, np.datetime64)

    dataset_df = dataset.time.to_dataframe()
    dataset_df.set_index('time', inplace=True)
    assert all(dataset_df.index.is_month_start == True), "time is not month start"
