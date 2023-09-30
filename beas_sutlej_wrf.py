"""
Raw and bias corrected (Bannister et al.) WRF output.
"""

import xarray as xr
import numpy as np
from scipy.interpolate import griddata
from tqdm import tqdm

import load.location_sel as ls
from load import data_dir


def collect_WRF(location: str or tuple, minyear: float, maxyear: float) -> xr.Dataset:
    """
    Load uncorrected WRF run data.

    Args:
        location (str or tuple): location string or lat/lon coordinate tuple
        minyear (float): start date in years
        maxyear (float): end date in years

    Returns:
        xr.DataArray: WRF data
    """
    wrf_ds = xr.open_dataset(data_dir + 'Bannister/Bannister_WRF_raw.nc')

    if type(location) == str:
        loc_ds = ls.select_basin(wrf_ds, location)
    else:
        lat, lon = location
        loc_ds = wrf_ds.interp(
            coords={"lon": lon, "lat": lat}, method="nearest")

    tim_ds = loc_ds.sel(time=slice(minyear, maxyear))
    ds = tim_ds.assign_attrs(plot_legend="WRF")
    return ds


def collect_BC_WRF(location: str or tuple, minyear: float, maxyear: float) -> xr.Dataset:
    """
    Load bias-corrected WRF run data. 

    Args:
        location (str or tuple): location string or lat/lon coordinate tuple
        minyear (float): start date in years
        maxyear (float): end date in years

    Returns:
        xr.DataArray: bias-corrected WRF data
    """

    bc_wrf_ds = xr.open_dataset(
        data_dir + 'Bannister/Bannister_WRF_corrected.nc')

    if type(location) == str:
        loc_ds = ls.select_basin(bc_wrf_ds, location)
    else:
        lat, lon = location
        loc_ds = bc_wrf_ds.interp(
            coords={"lon": lon, "lat": lat}, method="nearest")

    tim_ds = loc_ds.sel(time=slice(minyear, maxyear))
    ds = tim_ds.assign_attrs(plot_legend="Bias corrected WRF")
    return ds


def reformat_bannister_data():
    """ Project and save Bannister data on equal angle grid. """

    wrf_ds = xr.open_dataset(data_dir + 'Bannister/Bannister_WRF.nc')
    XLAT = wrf_ds.XLAT.values
    XLONG = wrf_ds.XLONG.values
    m_precip = wrf_ds.model_precipitation.values
    bias_corr_precip = wrf_ds.bias_corrected_precipitation.values
    time = wrf_ds.time.values

    ds = xr.Dataset(data_vars=dict(m_precip=(["time", "x", "y"], m_precip),
                    bias_corr_precip=(["time", "x", "y"], bias_corr_precip)),
                    coords=dict(lon=(["x", "y"], XLONG),
                    lat=(["x", "y"], XLAT), time=time))
    ds2 = ds.resample(time="MS").mean()
    #da2['time'] = da2.time.astype(float)/365/24/60/60/1e9 + 1970

    '''
    # Standardise time resolution
    maxyear = da2.time.max()
    minyear = da2.time.min()
    time_arr = np.arange(round(minyear) + 1./24., round(maxyear), 1./12.)
    da2['time'] = time_arr
    '''
    # Raw WRF data
    wrf_ds = ds2.drop('bias_corr_precip')
    wrf_ds = wrf_ds.rename({'m_precip': 'tp'})
    wrf_ds = interp(wrf_ds)
    wrf_ds.to_netcdf(data_dir + '/Bannister/Bannister_WRF_raw.nc')

    # Bias corrected WRF data
    bc_ds = ds2.drop('m_precip')
    bc_ds = bc_ds.rename({'bias_corr_precip': 'tp'})
    bc_ds = interp(bc_ds)
    bc_ds.to_netcdf(data_dir + 'Bannister/Bannister_WRF_corrected.nc')


def interp(ds):
    """ Interpolate to match sta to ERA5 grid."""

    # Generate a regular grid to interpolate the data
    x = np.arange(70, 85, 0.25)
    y = np.arange(25, 35, 0.25)
    grid_x, grid_y = np.meshgrid(y, x)

    # Create point coordinate pairs
    lats = ds.lat.values.flatten()
    lons = ds.lon.values.flatten()
    times = ds.time.values
    tp = ds.tp.values.reshape(len(times), -1)
    points = np.stack((lats, lons), axis=-1)

    # Linear interpolation
    grid_list = []
    for values in tp:
        grid_z0 = griddata(points, values, (grid_x, grid_y), method='linear')
        grid_list.append(grid_z0)
    interp_grid = np.array(grid_list)

    # Turn into xarray DataSet
    new_ds = xr.Dataset(data_vars=dict(
        tp=(["time", "lon", "lat"], interp_grid)),
        coords=dict(lon=(["lon"], x), lat=(["lat"], y),
                    time=(['time'], times)))
    return new_ds


def test_interp_grid(test_ds):
    """ Test that the interpolation grid is consistent. """

    indices_to_check = np.random.randint(0, 100, 10)

    lats = test_ds.lat.values.flatten()
    lons = test_ds.lon.values.flatten()
    times = test_ds.time.values
    tp = test_ds.tp.values.reshape(len(times), -1)
    points = np.stack((lats, lons), axis=-1)
    assert len(points) == tp.shape[1]

    for i in tqdm(indices_to_check):
        assert times[i] == test_ds.isel(time=i).time.values
        assert all(tp[i] == test_ds.sel(time=times[i]).tp.values.flatten())
    print('Done!')
