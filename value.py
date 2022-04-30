import os
import datetime
import numpy as np
import xarray as xr
import pandas as pd
import cdsapi

"""
VALUE dataset

"""

def formatting_data():
    
    # Import precipitation data
    df = pd.read_csv('data/VALUE/precip.txt')
    df = df.astype(float, errors='ignore')
    df['time'] = pd.to_datetime(df['YYYYMMDD'], format="%Y%m%d")
    df = df.drop(columns = ['YYYYMMDD'])
    
    # Resample
    df2 = df.resample('M', on='time').mean()
    time_arr = np.arange(1961 + 1./24., 2011, 1./12.)
    df2.index = time_arr
    df2 = df2.stack().reset_index()
    df2 = df2.rename({"level_0":'time', "level_1": "station_id", 0: "tp"}, axis=1)
    
    # Import station data and combine
    df4 = pd.read_csv('data/VALUE/stations.txt')
    df2['station_id'] = df2['station_id'].astype(int)
    df4['station_id'] = df4['station_id'].astype(int)
    df7 = df2.join(df4.set_index('station_id'), on='station_id')
    
    df7 = df7.rename({' name': 'name', ' longitude': 'lon', ' latitude': 'lat',
                      ' altitude': 'alt',}, axis=1)
    df7 = df7.drop([' source'], axis=1)
    df7.to_csv('data/VALUE/value_rsamp.csv')


def all_gauge_data(minyear, maxyear, threshold=None):
    """
    Download data between specified dates for all active stations between two
    dates.
    Can specify the treshold for the the total number of active days
    during that period:
    e.g. for 10 year period -> 4018 - 365 = 3653
    """

    filepath = 'data/VALUE/value_rsamp.csv'
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