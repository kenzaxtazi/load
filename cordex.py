import xarray as xr
import numpy as np
import datetime
import glob
from load import data_dir


def collect_CORDEX(domain: str, minyear: str, maxyear: str, experiment: str, rcm_model: str, gcm_model: str, freq='mon') -> xr.DataArray:
    """
    Collect CORDEX data and standardise time.

    Args:
        domain (str): CORDEX domain (EAS or WAS)
        minyear (str): minimum year of data
        maxyear (str): maximum year of data (exclusive)
        experiment (str): experiment name
        rcm_model (str): RCM model name
        gcm_model (str): GCM model name
        freq (str): frequency of data (mon or day)

    Returns:
        xr.DataArray: output CORDEX data
    """

    # generate list of files
    path = data_dir + "CORDEX/" + domain + "/" + freq + "/" + experiment + "/"
    all_files = glob.glob(path+'*')

    # sort files
    file_list = []
    for f in all_files:
        try:
            f_minyear = f.split("_")[-1].split('-')[-2][:4]
            f_maxyear = f.split("_")[-1].split('-')[-1][:4]
        except:
            print(f)

        if experiment in f:
            #print(experiment)
            if gcm_model in f:
                #print(gcm_model)
                if rcm_model in f:
                    #print(rcm_model)
                    if int(f_maxyear) > int(minyear):
                        if int(f_minyear) < int(maxyear):
                            file_list.append(f)

    # load data
    ds_list = []
    for f in file_list:
        ds = xr.open_dataset(f)
        ds['time'] = ds['time'].astype('datetime64[M]')
        ds_list.append(ds)

    # concatenate data
    cordex_ds = xr.concat(ds_list, 'time')
    cordex_ds = cordex_ds.sortby('time')
    cordex_ds = cordex_ds.assign_attrs(
        plot_legend="CORDEX " + domain + " " + gcm_model + " " + rcm_model + " " + experiment,)
    cordex_ds = cordex_ds.rename_vars({'pr': 'tp'})
    cordex_ds['tp'] *= 86400   # to mm/day
    sliced_cordex_ds = cordex_ds.sel(time=slice(minyear, maxyear))

    return  sliced_cordex_ds
