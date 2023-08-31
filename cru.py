"""
CRU dataset
"""

import datetime
import xarray as xr
import numpy as np


import load.location_sel as ls
from load import data_dir


def collect_CRU(location: str or tuple, minyear: str, maxyear: str) -> xr.DataArray:
    """
    Download interpolated data from CRU model.

    Args:
        location (str or tuple): location string or lat/lon coordinate tuple
        minyear (float): start date in years
        maxyear (float): end date in years

    Returns:
        xr.DataArray: Interpolated CRU data
    """
    cru_ds = xr.open_dataset(data_dir + "CRU/interpolated_cru_1901-2019.nc")

    if type(location) == str:
        loc_ds = ls.select_basin(cru_ds, location)
    else:
        lat, lon = location
        loc_ds = cru_ds.interp(
            coords={"lon": lon, "lat": lat}, method="nearest")

    tim_ds = loc_ds.sel(time=slice(minyear, maxyear))
    ds = tim_ds.assign_attrs(plot_legend="CRU")  # in mm/month
    return ds


def download():
    """ Return CRU data on a 0.25° by 0.25° grid."""

    extent = ls.basin_extent('indus')
    da = xr.open_dataset(data_dir + "CRU/cru_ts4.04.1901.2019.pre.dat.nc")
    da_cropped = da.sel(
        lon=slice(extent[1], extent[3]), lat=slice(extent[2], extent[0]))
    da_cropped['time'] = da_cropped['time'].astype("datetime64[M]")
    days_in_month = da_cropped.time.dt.days_in_month.values
    days_in_month_tiled = np.tile(
        days_in_month[:, np.newaxis, np.newaxis], (1, 30, 40))
    da_cropped['pre'] = da_cropped['pre'] / days_in_month_tiled  # mm/day
    #da_cropped['time'] = standardised_time(da_cropped)

    '''
    # Standardise time resolution
    maxyear = float(da_cropped.time.max())
    minyear = float(da_cropped.time.min())
    time_arr = np.arange(round(minyear) + 1./24., round(maxyear), 1./12.)
    '''

    da = da_cropped.rename_vars({'pre': 'tp'})
    x = np.arange(70, 85, 0.25)
    y = np.arange(25, 35, 0.25)
    interp_da = da.interp(lon=x, lat=y, method="nearest")
    interp_da.to_netcdf(data_dir + "CRU/interpolated_cru_1901-2019.nc")


def standardised_time(dataset: xr.DataArray) -> np.array:
    """
    FOR ARCHIVE ONLY - DO NOT USE

    Return array of standardised times to plot.

    Args:
        dataset (xr.DataArray):

    Returns:
        np.array: standardised time values
    """
    try:
        utime = dataset.time.values.astype(int)/(1e9 * 60 * 60 * 24 * 365)
    except Exception:
        time = np.array([d.strftime() for d in dataset.time.values])
        time2 = np.array([datetime.datetime.strptime(
            d, "%Y-%m-%d %H:%M:%S") for d in time])
        utime = np.array([d.timestamp() for d in time2]) / (60 * 60 * 24 * 365)
    return (utime + 1970)
