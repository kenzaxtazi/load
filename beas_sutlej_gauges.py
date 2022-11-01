"""
Raw gauge measurements from the Beas and Sutlej valleys
"""

from xmlrpc.client import boolean
import numpy as np
import pandas as pd
import xarray as xr
from math import floor, ceil
from load import data_dir


def gauge_download(station: str, minyear: float, maxyear: float) -> xr.DataArray:
    """
    Download and format raw gauge data.

    Args:
        station (str): station name (with first letter capitalised)
        minyear (float): start date in years
        maxyear (float): end date in years

    Returns:
        xr.DataArray: gauge precipitation values
    """
    filepath = data_dir + 'bs_gauges/RawGauge_BeasSutlej_.xlsx'
    daily_df = pd.read_excel(filepath, sheet_name=station)
    # daily_df.dropna(inplace=True)

    # To months
    daily_df.set_index('Date', inplace=True)
    daily_df.index = pd.to_datetime(daily_df.index)
    clean_df = daily_df.dropna()
    clean_df.loc[:, 'tp'] = pd.to_numeric(clean_df.tp, errors='coerce')
    df_monthly = clean_df.tp.resample('M').sum()/30.436875
    df = df_monthly.reset_index()
    df.loc[:, 'Date'] = df['Date'].values.astype(float)/365/24/60/60/1e9
    df.loc[:, 'Date'] = df['Date'] + 1970
    all_station_dict = pd.read_csv(
        data_dir + 'bs_gauges/gauge_info.csv', index_col='station').T

    # to xarray DataSet
    lat, lon, _elv = all_station_dict[station]
    df_ind = df.set_index('Date')
    da = df_ind.to_xarray()
    da = da.assign_attrs(plot_legend="Gauge data")
    da = da.assign_coords({'lon': lon})
    da = da.assign_coords({'lat': lat})
    da = da.rename({'Date': 'time'})

    # Standardise time resolution
    raw_maxyear = float(da.time.max())
    raw_minyear = float(da.time.min())
    time_arr = np.arange(floor(raw_minyear*12-1)/12 + 1. /
                         24., ceil(raw_maxyear*12-1)/12, 1./12.)
    da['time'] = time_arr

    tims_da = da.sel(time=slice(minyear, maxyear))
    return tims_da


def all_gauge_data(minyear: float, maxyear: float, threshold: int = None) -> xr.DataArray:
    """
    Download data between specified dates for all active stations between two dates.
    Can specify the minimum number of active days during that period:
    e.g. for 10 year period -> 4018 - 365 = 3653.

    Args:
        minyear (float): start date in years
        maxyear (float): end date in years
        threshold (int, optional): minimum number of active days. Defaults to None.

    Returns:
        xr.DataArray: gauge precipitation values
    """

    filepath = data_dir + "bs_gauges/qc_sushiwat_observations_MGM.xlsx"
    daily_df = pd.read_excel(filepath)

    maxy_str = str(maxyear) + '-01-01'
    miny_str = str(minyear) + '-01-01'
    mask = (daily_df['Date'] >= miny_str) & (daily_df['Date'] < maxy_str)
    df_masked = daily_df[mask]

    df_masked.set_index('Date', inplace=True)
    for col in list(df_masked):
        df_masked[col] = pd.to_numeric(df_masked[col], errors='coerce')

    if threshold is not None:
        df_masked = df_masked.dropna(axis=1, thresh=threshold)

    df_masked.index = pd.to_datetime(df_masked.index)
    df_monthly = df_masked.resample('M').sum()/30.436875
    df = df_monthly.reset_index()
    df['Date'] = df['Date'].values.astype(float)/365/24/60/60/1e9 + 1970

    df_ind = df.set_index('Date')
    da = df_ind.to_xarray()
    da = da.assign_attrs(plot_legend="Gauge data")
    da = da.rename({'Date': 'time'})

    # Standardise time resolution
    time_arr = np.arange(round(minyear) + 1./24., maxyear, 1./12.)
    da['time'] = time_arr
    return da
