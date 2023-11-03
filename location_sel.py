"""
Functions to help dowload data given
- Basin name
- Sub-basin name
- Coordinates
"""
import xarray as xr
from load import data_dir


def select_basin(dataset, location):
    """ Interpolate dataset at given coordinates """
    mask_filepath = find_mask(location)
    if mask_filepath is None:
        basin = dataset
    else:
        basin = apply_mask(dataset, mask_filepath)
    return basin


def find_mask(location):
    """ Returns a mask filepath for given location """
    mask_dic = {'ngari': data_dir + 'Masks/Ngari_mask.nc',
                'khyber': data_dir + 'Masks/Khyber_mask.nc',
                'gilgit': data_dir + 'Masks/Gilgit_mask.nc',
                'uib':  data_dir + 'Masks/ERA5_Upper_Indus_mask.nc',
                'sutlej':  data_dir + 'Masks/Sutlej_mask.nc',
                'beas':  data_dir + 'Masks/Beas_mask.nc',
                'beas_sutlej':  data_dir + 'Masks/Beas_Sutlej_mask.nc',
                'hma': None,
                'korea': None,
                'france': None,
                'value': None,
                'indus': None}
    mask_filepath = mask_dic[location]
    return mask_filepath


def basin_finder(loc):
    """
    Finds basin to load data from.
    Input
        loc: list of coordinates [lat, lon] or string refering to an area.
    Output
        basin , string: name of the basin.
    """
    basin_dic = {'indus': 'indus', 'uib': 'indus', 'sutlej': 'indus',
                 'beas': 'indus', 'beas_sutlej': 'indus', 'khyber': 'indus',
                 'ngari': 'indus', 'gilgit': 'indus', 'france': 'france',
                 'korea': 'korea', 'value': 'value', 'europe': 'value'}
    if type(loc) is str:
        basin = basin_dic[loc]
        return basin
    if type(loc) is not str:  # fix to search with coords
        print('Not a string')


def apply_mask(data, mask_filepath):
    """
    Opens NetCDF files and applies mask to data can also interp data to mask
    grid.
    Inputs:
        data (filepath string or NetCDF)
        mask_filepath (filepath string)
        interp (boolean): nearest-neighbour interpolation
    Return:
        A Data Array
    """
    if data is str:
        da = xr.open_dataset(data)
        if "expver" in list(da.dims):
            print("expver found")
            da = da.sel(expver=1)
    else:
        da = data
    mask = xr.open_dataset(mask_filepath)
    mask = mask.rename({'latitude': 'lat', 'longitude': 'lon'})
    mask_da = mask.overlap

    try:
        masked_da = da.where(mask_da > 0, drop=True)
    except Exception:
        interp_da = da.interp_like(mask_da)
        masked_da = interp_da.where(mask_da > 0, drop=True)
    return masked_da


def basin_extent(string):
    """ Returns extent of basin to save data """
    basin_dic = {'indus': [40, 65, 25, 85],
                 'hma': [42, 60, 20, 110],
                 'france': [48, -2, 41, 10],
                 'korea': [39, 124, 33, 131],
                 'value': [71, -10, 36, 32]}
    return basin_dic[string]
