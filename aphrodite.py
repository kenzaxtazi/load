"""
The APHRODITE datasets over Monsoon Asia:
- V1101 from 1951 to 2007,
- V1101_EXR from 2007-2016.
Precipiation is in mm/day.
"""

import glob
import numpy as np
import xarray as xr
from tqdm import tqdm
from pwd import pwd
import location_sel as ls


def collect_APHRO(location: str or tuple, minyear: float, maxyear: float) -> xr.DataArray:
    """
    Download data from APHRODITE model.

    Args:
        location (str or tuple): location string or lat/lon coordinate tuple
        minyear (float): start date in years
        maxyear (float): end date in years

    Returns:
        xr.DataArray: APHRODITE data
    """

    aphro_da = xr.open_dataset(
        pwd + "data/APHRODITE/aphrodite_indus_1951_2016.nc")

    if type(location) == str:
        loc_da = ls.select_basin(aphro_da, location)
    else:
        lat, lon = location
        loc_da = aphro_da.interp(coords={"lon": lon, "lat": lat},
                                 method="nearest")

    tim_da = loc_da.sel(time=slice(minyear, maxyear))
    da = tim_da.assign_attrs(plot_legend="APHRODITE")  # in mm/day
    return da


def merge_og_files():
    """Function to open, crop and merge the raw APHRODITE data files."""

    da_list = []
    extent = ls.basin_extent('indus')

    print('1951-2007')
    for f in tqdm(glob.glob(
            pwd + 'data/APHRODITE/APHRO_MA_025deg_V1101.1951-2007.gz/*.nc')):
        da = xr.open_dataset(f)
        da = da.rename({'latitude': 'lat', 'longitude': 'lon', 'precip': 'tp'})
        da_cropped = da.tp.sel(lon=slice(extent[1], extent[3]),
                               lat=slice(extent[2], extent[0]))
        da_resampled = (da_cropped.resample(time="M")).mean()
        da_resampled['time'] = da_resampled.time.astype(float)/365/24/60/60/1e9
        da_resampled['time'] = da_resampled['time'] + 1970
        da_list.append(da_resampled)

    print('2007-2016')
    for f in tqdm(
            glob.glob(pwd + 'data/APHRODITE/APHRO_MA_025deg_V1101_EXR1/*.nc')):
        da = xr.open_dataset(f)
        da = da.rename({'precip': 'tp'})
        da_cropped = da.tp.sel(lon=slice(extent[1], extent[3]),
                               lat=slice(extent[2], extent[0]))
        da_resampled = (da_cropped.resample(time="M")).mean()
        da_resampled['time'] = da_resampled.time.astype(float)/365/24/60/60/1e9
        da_resampled['time'] = da_resampled['time'] + 1970
        da_list.append(da_resampled)

    da_merged = xr.merge(da_list)

    # Standardise time resolution
    maxyear = float(da_merged.time.max())
    minyear = float(da_merged.time.min())
    time_arr = np.arange(round(minyear) + 1./24., round(maxyear), 1./12.)
    da_merged['time'] = time_arr

    da_merged.to_netcdf(pwd + "data/APHRODITE/aphrodite_indus_1951_2016.nc")
