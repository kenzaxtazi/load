"""
Raw and bias corrected (Bannister et al.) WRF output.
"""

import xarray as xr
import numpy as np
from scipy.interpolate import griddata

import location_sel as ls


def collect_WRF(location: str or tuple, minyear: float, maxyear: float) -> xr.DataArray:
    """
    Load uncorrected WRF run data.

    Args:
        location (str or tuple): location string or lat/lon coordinate tuple
        minyear (float): start date in years
        maxyear (float): end date in years

    Returns:
        xr.DataArray: WRF data
    """
    wrf_da = xr.open_dataset(pwd + 'data/Bannister/Bannister_WRF_raw.nc')

    if type(location) == str:
        loc_da = ls.select_basin(wrf_da, location)
    else:
        lat, lon = location
        loc_da = wrf_da.interp(
            coords={"lon": lon, "lat": lat}, method="nearest")

    tim_da = loc_da.sel(time=slice(minyear, maxyear))
    da = tim_da.assign_attrs(plot_legend="WRF")
    return da


def collect_BC_WRF(location: str or tuple, minyear: float, maxyear: float) -> xr.DataArray:
    """
    Load bias-corrected WRF run data. 

    Args:
        location (str or tuple): location string or lat/lon coordinate tuple
        minyear (float): start date in years
        maxyear (float): end date in years

    Returns:
        xr.DataArray: bias-corrected WRF data
    """

    bc_wrf_da = xr.open_dataset(
        pwd + 'data/Bannister/Bannister_WRF_corrected.nc')

    if type(location) == str:
        loc_da = ls.select_basin(bc_wrf_da, location)
    else:
        lat, lon = location
        loc_da = bc_wrf_da.interp(
            coords={"lon": lon, "lat": lat}, method="nearest")

    tim_ds = loc_da.sel(time=slice(minyear, maxyear))
    da = tim_ds.assign_attrs(plot_legend="Bias corrected WRF")
    return da


def reformat_bannister_data():
    """ Project and save Bannister data on equal angle grid."""

    wrf_da = xr.open_dataset(pwd + 'data/Bannister/Bannister_WRF.nc')
    XLAT = wrf_da.XLAT.values
    XLONG = wrf_da.XLONG.values
    m_precip = wrf_da.model_precipitation.values
    bias_corr_precip = wrf_da.bias_corrected_precipitation.values
    time = wrf_da.time.values

    da = xr.Dataset(data_vars=dict(m_precip=(["time", "x", "y"], m_precip),
                    bias_corr_precip=(["time", "x", "y"], bias_corr_precip)),
                    coords=dict(lon=(["x", "y"], XLONG),
                    lat=(["x", "y"], XLAT), time=time))
    da2 = (da.resample(time="M")).mean()
    da2['time'] = da2.time.astype(float)/365/24/60/60/1e9 + 1970

    # Standardise time resolution
    maxyear = da2.time.max()
    minyear = da2.time.min()
    time_arr = np.arange(round(minyear) + 1./24., round(maxyear), 1./12.)
    da2['time'] = time_arr

    # Raw WRF data
    wrf_da = da2.drop('bias_corr_precip')
    wrf_da = wrf_da.rename({'m_precip': 'tp'})
    wrf_da = interp(wrf_da)
    wrf_da.to_netcdf(pwd + 'data/Bannister/Bannister_WRF_raw.nc')

    # Bias corrected WRF data
    bc_da = da2.drop('m_precip')
    bc_da = bc_da.rename({'bias_corr_precip': 'tp'})
    bc_da = interp(bc_da)
    bc_da.to_netcdf(pwd + 'data/Bannister/Bannister_WRF_corrected.nc')


def interp(da):
    """ Interpolate to match dsta to ERA5 grid."""

    # Generate a regular grid to interpolate the data
    x = np.arange(70, 85, 0.25)
    y = np.arange(25, 35, 0.25)
    grid_x, grid_y = np.meshgrid(y, x)

    # Create point coordinate pairs
    lats = da.lat.values.flatten()
    lons = da.lon.values.flatten()
    times = da.time.values
    tp = da.tp.values.reshape(396, -1)
    points = np.stack((lats, lons), axis=-1)

    # Interpolate using nearest neigbours
    grid_list = []
    for values in tp:
        grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
        grid_list.append(grid_z0)
    interp_grid = np.array(grid_list)

    # Turn into xarray DataSet
    new_da = xr.Dataset(data_vars=dict(
        tp=(["time", "lon", "lat"], interp_grid)),
        coords=dict(lon=(["lon"], x), lat=(["lat"], y),
                    time=(['time'], times)))
    return new_da
