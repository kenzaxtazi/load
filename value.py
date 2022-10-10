import os
import datetime
import numpy as np
import xarray as xr
import pandas as pd

"""
VALUE dataset

"""


def formatting_data(monthly=True):
    """
    Create new file with data in useable format. 

    Args:
        monthly (bool, optional): whether to resample to monthly data. Defaults to True.
    """

    # Import precipitation data
    df = pd.read_csv(
        '/Users/kenzatazi/Documents/CDT/Code/data/VALUE_ECA_86_v2/precip.txt')
    df = df.astype(float, errors='ignore')
    df['time'] = pd.to_datetime(df['YYYYMMDD'], format="%Y%m%d")
    df = df.drop(columns=['YYYYMMDD'])

    # Resample
    if monthly == True:
        df2 = df.resample('M', on='time').mean()
        time_arr = np.arange(1961 + 1./24., 2011, 1./12.)
        df2.index = time_arr
        df2 = df2.stack().reset_index()
    if monthly == False:
        df2 = df.resample('D', on='time').mean()
        time_arr = year_into_days(1961, 2011)
        df2.index = time_arr
        df2 = df2.stack().reset_index()
        df2 = df2[:-1]
    df2 = df2.rename(
        {"level_0": 'time', "level_1": "station_id", 0: "tp"}, axis=1)

    # Import station data and combine
    df4 = pd.read_csv('/Users/kenzatazi/Documents/CDT/Code/ddata/VALUE_ECA_86_v2/stations.txt',
                      sep='\t', lineterminator='\r')
    df2['station_id'] = df2['station_id'].astype(int)
    df4['station_id'] = df4['station_id'].astype(int)
    df7 = df2.join(df4.set_index('station_id'), on='station_id')

    df7 = df7.rename({' name': 'name', ' longitude': 'lon', ' latitude': 'lat',
                      ' altitude': 'alt', }, axis=1)
    df7 = df7.drop(['source'], axis=1)

    if monthly == True:
        df7.to_csv(
            '/Users/kenzatazi/Documents/CDT/Code/data/VALUE_ECA_86_v2/value_rsamp.csv')
    if monthly == False:
        df7.to_csv(
            '/Users/kenzatazi/Documents/CDT/Code/data/VALUE_ECA_86_v2/value_daily.csv')


def all_gauge_data(minyear: float, maxyear: float, threshold=None, monthly=True) -> pd.DataFrame:
    """    
    Download data between specified dates for all active stations between two dates.
    Can specify threshold for the the total number of active days during period:
            e.g. for 10 year period -> 4018 - 365 = 3653

    Args:
        minyear (float): start year
        maxyear (float): end year
        threshold (_type_, optional): threshold value. Defaults to None.
        monthly (bool, optional): whether to return monthly or daily data. Defaults to True.

    Returns:
        pd.DataFrame: VALUE data
    """
    if monthly == True:
        filepath = '/Users/kenzatazi/Documents/CDT/Code/data/VALUE_ECA_86_v2/value_rsamp.csv'
    if monthly == False:
        filepath = '/Users/kenzatazi/Documents/CDT/Code/data/VALUE_ECA_86_v2/value_daily.csv'
    df = pd.read_csv(filepath)
    df = df.drop(['Unnamed: 0'], axis=1)
    mask = (df['time'] >= minyear) & (df['time'] < maxyear)
    df_masked = df[mask]

    return df_masked


def gauge_download(station, minyear, maxyear):
    """
    Download and format raw gauge data

    Args:
        station (str): station name (capitalised)
    Returns
       df (pd.DataFrame): precipitation gauge values
    """
    df = all_gauge_data(minyear, maxyear)
    station_df = df[df['name'] == station]

    return station_df


def year_into_days(start_year: float, end_year: float) -> np.array:
    """Divide years into days

    Args:
        start_year (float): year to start array
        end_year (float): year to end array

    Returns:
        np.array: array in years with daily resolution 
    """
    final_arr = np.array([])
    year_arr = np.arange(start_year, end_year)
    for y in year_arr:
        if y % 4 < 0.001:
            year_in_days_arr = np.arange(y, y+1, 1/366)
        else:
            year_in_days_arr = np.arange(y, y+1, 1/365)
        final_arr = np.append(final_arr, year_in_days_arr)
    return final_arr
