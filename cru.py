"""
CRU dataset
"""

import datetime
import xarray as xr
import numpy as np


import location_sel as ls


def collect_CRU(location: str or tuple, minyear: float, maxyear: float) -> xr.DataArray:
    """
    Download interpolated data from CRU model.

    Args:
        location (str or tuple): location string or lat/lon coordinate tuple
        minyear (float): start date in years
        maxyear (float): end date in years

    Returns:
        xr.DataArray: Interpolated CRU data
    """
    cru_da = xr.open_dataset("data/CRU/interpolated_cru_1901-2019.nc")

    if type(location) == str:
        loc_da = ls.select_basin(cru_da, location)
    else:
        lat, lon = location
        loc_da = cru_da.interp(
            coords={"lon": lon, "lat": lat}, method="nearest")

    tim_da = loc_da.sel(time=slice(minyear, maxyear))
    da = tim_da.assign_attrs(plot_legend="CRU")  # in mm/month
    return da


def download():
    """ Return CRU data on a 0.25° by 0.25° grid."""

    extent = ls.basin_extent('indus')
    da = xr.open_dataset("data/CRU/cru_ts4.04.1901.2019.pre.dat.nc")
    da_cropped = da.sel(
        lon=slice(extent[1], extent[3]), lat=slice(extent[2], extent[0]))
    da_cropped['pre'] /= 30.437  # TODO apply proper function to get mm/day
    da_cropped['time'] = standardised_time(da_cropped)

    # Standardise time resolution
    maxyear = float(da_cropped.time.max())
    minyear = float(da_cropped.time.min())
    time_arr = np.arange(round(minyear) + 1./24., round(maxyear), 1./12.)
    da_cropped['time'] = time_arr

    da = da_cropped.rename_vars({'pre': 'tp'})
    x = np.arange(70, 85, 0.25)
    y = np.arange(25, 35, 0.25)
    interp_da = da.interp(lon=x, lat=y, method="nearest")
    interp_da.to_netcdf("data/CRU/interpolated_cru_1901-2019.nc")


def standardised_time(dataset: xr.DataArray) -> np.array:
    """
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
