# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 16:50:55 2021

@author: KinzCode
"""


import pandas as pd
import json
import numpy as np
import datetime
import time

from copy import deepcopy
from cols import all_cols, fight_stat_cols, numerical_fight_stat_cols, time_fight_stat_cols


def get_sec(time_str):
    """
    Parameters
    ----------
    time_str : a string signfiying a time variable in the format of %M:%S and %M:%S:%MS.

    Returns
    -------
    s: the string converted to a seconds based numerical variable. 200 = 200 seconds 
    """
   
    try:
      # Handle both minute:seconds and minute:seconds:milliseconds
      m, s = time_str.split(":")[:2]
    except ValueError:
      s = 0
    else:
      s = int(m) * 60 + int(s)
    return s


def clean_numerical_data(df):
    """
    Parameters:
    -----------
    df : takes in the raw fighter data csv
    
    Returns:
    --------
    df : returns a clean df with no special characters in the numerical data,
    as well as transforming time statistics from a string in %M:%S format to a
    seconds variable (200 = 200 seconds)
    
    """
    df = df.replace("[*]", "", regex = True)
    
    df[time_fight_stat_cols] = df[time_fight_stat_cols].applymap(get_sec)

    return df
    

def merge_data(fighter_data, fighter_results, event_date_location):
    """
    Parameters:
    -----------
    fighter_data: a cleaned df containing matchups and the strikes attempted, landed etc of the fighters
    fighter_results: a df containing the results of the fights from the above df
    event_data_location: a df containging information of where fights were held and the dates
    
    Returns:
    --------
    fighter_data: the function merges onto the fighter_data dataframe and returns a single df
    
    """
    fighter_results.rename(columns = {"Fighter_Name": 'RedCorner'}, inplace = True)
    #reduce df to name and win and fightId for merge
    fighter_results = fighter_results[['FightID', 'RedCorner', 'Result', 'Method']]
    #merge on to red corner. All fights are looked at as Redcorner being the A side so if result is
    # "Lost" fighter in blue corner won.
    fighter_data = fighter_data.merge(fighter_results, on = ['FightID', 'RedCorner'], how = 'left')
    
    fighter_data = fighter_data.merge(event_date_location, on = ['EventID'], how = 'left')
    
    fighter_data['Date'] = pd.to_datetime(fighter_data['Date'], format="%d/%m/%Y").dt.date
    fighter_data['Date'] = pd.to_datetime(fighter_data['Date'])
    fighter_data['FightYear'] = fighter_data['Date'].dt.year
    
    fighter_data = fighter_data.sort_values('FightID', ascending=True)
    return fighter_data        


def merge_historical_odds(df, pinnacle_historical_odds):
    """
    Parameters:
    -----------
    df: a groupby object of the fighter_data df grouped by "EventID'"
    pinnacle_historical_odds: a dictionary with EventID as keys holding historic market data
    
    Returns:
    --------
    df: the hisotric market data is mapped to the respective RedOdds/BlueOdds columns
    
    """
    try:
        pinnacle_historical_odds = pinnacle_historical_odds[str(df['EventID'].max())]
        df['RedOdds'] = (df['RedCorner'].map(pinnacle_historical_odds)).astype(float)
        df['BlueOdds'] = (df['BlueCorner'].map(pinnacle_historical_odds)).astype(float)
    except KeyError:
        df['RedOdds'] = np.nan
        df['BlueOdds'] = np.nan
    return df


if __name__ == '__main__':
    ###Read in raw csv files
    #fighter data with all raw stats. Each line is an individual fight consisting of 2 fighters
    fighter_data = pd.read_csv('dat/fighter_data.csv')
    #Results of fights
    fighter_results = pd.read_csv('dat/fighter_results_dates.csv')
    #Contains data and venue information of where fights were held.
    event_date_location = pd.read_csv('dat/event_date_location.csv', encoding='ISO-8859-1')
    #Historical pinnacle closing line odds
    with open('dat/historical_pinnacle_odds2.json') as json_file:
        pinnacle_historical_odds = json.load(json_file)
    
    
    #clean numbers, remove asteric, change to float
    fighter_data = clean_numerical_data(fighter_data)
    
    
    #merge data
    fighter_data = merge_data(fighter_data, fighter_results, event_date_location)
    
    #merge historical odds to clean data
    fighter_data['EventID2'] = fighter_data['EventID']
    fighter_data = fighter_data.groupby('EventID').apply(merge_historical_odds, pinnacle_historical_odds)
    
    #drop bad data where there is missing names and weightclass information
    fighter_data = fighter_data[fighter_data['RedCorner'].notna()]
    fighter_data = fighter_data[fighter_data['WeightClass'].notna()]
    
    #save cleaned df
    fighter_data.to_csv('dat/cleaned_df.csv', index = False)

    
        