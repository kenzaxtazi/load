import xarray as xr
import numpy as np
import datetime
from load import data_dir

def collect_CORDEX() -> xr.DataArray:
    """
    Downloads data from CORDEX East Asia model.

    Returns:
        xr.DataArray: CORDEX East Asia data
    """

    cordex_90_da = xr.open_dataset(
        data_dir + "cordex/pr_EAS-44i_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-"
        "HadRM3P_v1_mon_199001-199012.nc")
    cordex_91_00_da = xr.open_dataset(
        data_dir + "cordex/pr_EAS-44i_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-"
        "HadRM3P_v1_mon_199101-200012.nc")
    cordex_01_da = xr.open_dataset(
        data_dir + "cordex/pr_EAS-44i_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-"
        "HadRM3P_v1_mon_200101-201012.nc")
    cordex_02_11_da = xr.open_dataset(
         data_dir + "/cordex/pr_EAS-44i_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-"
        "HadRM3P_v1_mon_201101-201111.nc")
    cordex_90_00_da = cordex_90_da.merge(cordex_91_00_da)
    cordex_01_11_da = cordex_01_da.merge(cordex_02_11_da)
    cordex_da = cordex_01_11_da.merge(cordex_90_00_da)  # in kg/m2/s
    cordex_da = cordex_da.assign_attrs(
        plot_legend="CORDEX EA - MOHC-HadRM3P historical")
    cordex_da = cordex_da.rename_vars({'pr': 'tp'})
    cordex_da['tp'] *= 60 * 60 * 24   # to mm/day
    cordex_da['time'] = standardised_time(cordex_da)

    return cordex_da


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
        utime = np.array([d.timestamp()
                          for d in time2]) / (60 * 60 * 24 * 365)
    return (utime + 1970)
