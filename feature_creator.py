# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 13:18:08 2021

@author: KinzCode
"""

import pdb, traceback, sys
import pandas as pd
import numpy as np
import json

from datetime import datetime
from copy import deepcopy 


from cols import  fight_stat_cols, no_corner_fight_stat_cols, summed_cols

  

def create_fighters_and_divisions_list(df):
    """
    Parameters
    ----------
    df : takes in the cleaned df containing all the fighters stats

    Returns
    -------
    fighters_list : a list of unique fighter names within the data set.
    divisions_list : a list of unique weight divisions within the data set.

    """
    
    fighters_list = list(set(list(set(df['RedCorner'])) + list(set(df['BlueCorner']))))
    
    divisions_list = list(df['WeightClass'].unique())
    
    return fighters_list, divisions_list


def create_fight_tally_dict(df, fighters_list):
    """
    Parameters
    ----------
    df : takes in the cleaned df containing all the fighters stats.
    fighters_list : a list of unique fighter names within the data set

    Returns
    -------
    fight_tally_dict: a dictionary containing each fighter as a key with the
                        total amount of fights they have had within the data set
    
    fight_tally_by_fight_id: a dictionary with fighter name as keys containing 
                            more dictionaries inside with keys of every fight ID
                            containing how many fights the fighter had had within the
                            dataset previous to that fight

    """
    
    fight_tally_dict = {}
    fight_tally_by_fight_id = {i : {} for i in fighters_list}
    
    for fighter in fighters_list:
        loop_df = (df[(df['RedCorner'] == fighter) |
                     (df['BlueCorner'] == fighter)])
        
        number_of_fights = len(loop_df)
        
        fights_range = list(range(number_of_fights))
        loop_df['FightTally'] = fights_range
        fight_tally_by_fight_id[fighter].update(dict(zip(loop_df['FightID'], 
                                                loop_df['FightTally'])))
        
        
        fight_tally_dict.update({fighter:number_of_fights})
        
    return fight_tally_dict, fight_tally_by_fight_id



def _map_previous_divisions_and_last_year_fights(row, fight_id_previous_fights_dict, 
                                                 fights_last_year_dict):
    
    """
    Parameters
    ----------
    row : Takes in a row which has a unique "FightID"
    fight_id_previous_fights_dict : A dictionary with Unique "FightID" as key within 2 other dicts,
        wither fighter name as keys holding a int value, reflective of the number of previous fights
        that fighter has fought within the data set.
    fights_last_year_dict : A dictionary with Unique "FightID" as key within 2 other dicts,
        wither fighter name as keys holding a int value, reflective of the number of previous fights
        that fighter has fought within the previous year to the respective FightID.

    Returns
    -------
    row : Returns row with mapped values to the newly created columns

    """
    #reset index, to access FightID 
    row = row.reset_index(drop = True)
    fight_id = row['FightID'][0]
    
    #loop over corners
    for colour in ['Red', 'Blue']:
        #access values within the dict
        prev_division = fight_id_previous_fights_dict[fight_id][row[f'{colour}Corner'][0]]
        fights_last_year = fights_last_year_dict[fight_id][row[f'{colour}Corner'][0]]
        
        #Create new columns and assign values 
        row[f'{colour}CornerPreviousDivision'] = prev_division
        row[f'{colour}CornerPreviousYearsFights'] = fights_last_year
    return row    
        

    
    
def create_previous_division_feature(df, fighters_list):
    """

    Parameters
    ----------
    df : takes in the cleaned df containing all the fighters stats.
    fighters_list : a list of unique fighter names within the data set

    Returns
    -------
    df : same dataframe with new columns dispalying the weight division each figh previously fought in 
        e.g. df['RedCornerPreviousDivision'] and the amount of times they had fought within the last year.
    
    Additional
    -------
    
    """
    
    """ 
    # Feature is designed to at each fight show what previous weight class 
    # a fighter fought at so that if they have moved up a weight division
    # for a super fight or to try something new their rating doesnt get punished
    # if they lose. Weightclasses will be given a rating 1 being the lightest 
    # and X being the heaviest.
    """
    
    division_map = {
        'Flyweight': 1,
        'Bantamweight': 2,
        'Featherweight': 3,
        'Lightweight': 4,
        'Welterweight': 5, 
        'Middleweight': 6,
        'Light Heavyweight': 7,
        'Heavyweight': 8, 
        "Women's Strawweight": 1,
        "Women's Flyweight": 2, 
        "Women's Bantamweight": 3,
        "Women's Featherweight": 4,
        np.nan: 0, 
        'Catch Weight':0
        }
    

    
    fight_id_previous_fights_dict = {i: {}  for i in list(df['FightID'].unique())}
    fights_last_year_dict = {i: {}  for i in list(df['FightID'].unique())}
    
    # map weightclass values for outbound df
    df['WeightClass'] = df['WeightClass'].map(division_map)
    
    #loop over all fighters within data set
    for fighter in fighters_list:
        loop_frame = df

        loop_frame = loop_frame[(loop_frame['RedCorner'] == fighter) |
                                 (loop_frame['BlueCorner'] == fighter)]
        
        loop_frame = loop_frame.reset_index(drop = True)
        
        #create fighter activity
        last_years_fights = create_fighter_activity(loop_frame)
        
        #create_rolling_sums
        rolling_means = create_rolling_sums(loop_frame, fighter)
        
        # need to hack first entry in previous weight
        first_entry = loop_frame['WeightClass'][0]
        loop_frame['PreviousWeight'] = loop_frame['WeightClass'].shift(1)
        #insr initial value after shift forward
        loop_frame.at[0, 'PreviousWeight'] = first_entry
        
        #loop thorugh filtered dict and update dict with createdd data
        for index, row in loop_frame.iterrows():
            
            if row['RedCorner'] == fighter:
                 fight_id_previous_fights_dict[(row['FightID'])].update({fighter:row['PreviousWeight']})
                 fights_last_year_dict[(row['FightID'])].update({fighter:row['FightsLastYear']})
            
            elif row['BlueCorner'] == fighter:
                fight_id_previous_fights_dict[row['FightID']].update({fighter:row['PreviousWeight']})
                fights_last_year_dict[(row['FightID'])].update({fighter:row['FightsLastYear']})
    
    
    df['FightID2'] = df['FightID']
    #groupby each individual fight and map the appropriate data.
    df = df.groupby('FightID2').apply(_map_previous_divisions_and_last_year_fights, fight_id_previous_fights_dict, fights_last_year_dict)
    
    return df
             
                
def create_fighter_activity(df):
    """
    Parameters
    ----------
    df : Takes in a df filtered by a SINGLE fighter_name string, dispalying all of that fighters fights within
        the dataset.

    Returns
    -------
    df : The same df with a new variable "FightsLastYear" which displays how many fights that fighter has had
        within the last year at the given time of the FightID

    """
    #convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    #create list of unique dates within filtered df
    dates_list = [i for i in df.Date]
    
    dates = []
    number_of_fights = []
    
    #filter df by unique dates and count number of fights between date and year prior
    for date in dates_list:
        year_before = (date  - pd.DateOffset(years=1))
        
        date_frame = df[(df['Date'] < date) &
                        (df['Date'] >= year_before)]
         
       
        #length of df = how many fights within last year
        number_fights_last_year = len(date_frame)
        

        
        dates.append(date)
        number_of_fights.append(number_fights_last_year)
    
    #create dict with date and numer of fighs within last year to that date

    last_year_fights = dict(zip(dates,number_of_fights))
    
    #map variable to new column on the date.
    df['FightsLastYear'] = df['Date'].map(last_year_fights)         
    return df


def _create_means(df, stat_dict):
    """
    Parameters
    ----------
    df : Takes in a groupby object, groupbed by all the weightclasses in the dataset
    stat_dict : a dictionary with the different weightclasses within the data set as keys, holding
                more dictionaries with the fight stats as keys that hold and empty dict
    Returns
    -------
    stat_dict : puts a mean value in the empty dict

    """
    df = df.reset_index(drop = True)
    # df.dropna(inplace = True)
    weight_class = str(df['WeightClass'][0])
    for col in no_corner_fight_stat_cols:
        stat_mean = (df[f'Red_{col}'] + df[f'Blue_{col}']).mean()
        stat_dict[weight_class][col] = stat_mean
    return stat_dict


def mean_stats_by_weight(df, division_list):
    """

    Parameters
    ----------
    df : takes in a cleaned df with each line a unique fight and set of stats
    division_list : a list of unique strings, identifying the weight divisions within the dataset
    Returns
    -------
    stat_dict : a dict with weight divisions as keys holding dicts with the fight stat as a key
                holding a mean value for that stat withing that devision
                
                e.g. {welterweight : {strike_attempts: 2}, {strikes_landed: 1}}

    """
    #division_list = list(df['WeightClass'].unique())
    stat_dict = {i : {i : "" for i in no_corner_fight_stat_cols} for i in division_list}
    df['WeightClass2'] = df['WeightClass']
    df.groupby('WeightClass2').apply(_create_means, stat_dict)
    return stat_dict

def create_rolling_columns(df, window_range, column_labels):
    """
    Parameters
    ----------
    df : Takes in the constructed rolling_df. Where each row has a unique FightID and has the
        hero and villain data associated to it for the focused fighter.
    window_range : User defined int which determines how many windows to roll for each variable.
    column_labels : the column labels imported from cols.py
    
    Returns
    -------
    df : the origonal df with the new rolling features.

    """
    window_range_list = list(range(1, window_range + 1))
    for window in window_range_list:
        df = deepcopy(df)
        for col in column_labels:
            df[f'{col}_window_{window}'] = df[col].shift(1).rolling(window=window,center=False).mean()
    
    return df


def calculate_sums(row, hero_cols, villain_cols):
    """
    Parameters
    ----------
    row : Takes in a row from the looped df. Each row is 1 unique fight
    hero_cols : The column title that applies to the focused fighter. E.g. if
                fighter is in RedCorner , will inclue Red_Punch_Attempts
    villain_cols :  The column title that does not apply to the focused fighter. E.g. if
                focused fighter is in RedCorner , will inclue Blue_Punch_Attempts

    Returns
    -------
    values_list : A list containing the created summed variables for the hero and villain.

    """
    
    hero = row.reindex(index = hero_cols)
    villain = row.reindex(index = villain_cols)
    
    hero_list = []
    villain_list = []
    for var in ['Attempts', 'Landed', 'Time']:
        hero_loop = hero[[i for i in hero_cols if var in i]]
        villain_loop = villain[[i for i in villain_cols if var in i]]
        
        hero_sum = hero_loop.sum()
        villain_sum = villain_loop.sum()
        
        hero_list.append(hero_sum)
        villain_list.append(villain_sum)

    values_list = hero_list + villain_list

    return values_list    

    
    

def create_rolling_sums(df, fighter_name):
    """

    Parameters
    ----------
    df : Takes in a df filtered by a SINGLE fighter_name string, dispalying all of that fighters fights within
        the dataset.
    fighter_name : The fighters name string variable that is filtering the df.

    Returns
    -------
    Function updates fighters_stats_dict with 3 rolling variables for the hero and villain
    fight_stat_cols

    """
    
    #create list to append created stat values to
    fighter_list = []
    #fighter will switch between blue and red corner in each fight
    #loop through df and apply criteria based upon which corner fighter in
    for index, row in df.iterrows():
        hero_list = [(row['FightID'])]
        
        #hero cols are whatever corner the focused fighter is in
        #Villain cols are whatever corner the non focused fighter is in
        
        if row['RedCorner'] == fighter_name:
            hero_cols = [i for i in fight_stat_cols if 'Red_' in i]
            villain_cols = [i for i in fight_stat_cols if 'Blue_' in i]
        
            values_list = calculate_sums(row, hero_cols, villain_cols)
            
            for value in values_list:
                hero_list.append(value)
            
        elif row['BlueCorner'] == fighter_name:
            hero_cols = [i for i in fight_stat_cols if 'Blue_' in i]
            villain_cols = [i for i in fight_stat_cols if 'Red_' in i]
            
            values_list = calculate_sums(row, hero_cols, villain_cols)
            
            for value in values_list:
                hero_list.append(value)
        
        #Append
        fighter_list.append(hero_list) 
            
    #Create df with calculated rolling variables appended to fighter_list
    #Colummns are Fight_ID + summed_cols imported from the cols.py script
    #values in fighter_list are in same order as rolling_df columns
    #due to construct of previous cfunctions
    rolling_df = pd.DataFrame(fighter_list, columns = (['FightID'] + summed_cols))
  
    #create rolling feature
    rolling_df = create_rolling_columns(rolling_df, 3, summed_cols)
    

    #convert df to dictionary
    rolling_df.set_index('FightID', inplace=True)
    rolling_dict = rolling_df.to_dict('index')
    fighters_stats_dict[fighter_name].update(rolling_dict)
    
         


if __name__ == '__main__':
    #print start time as script takes ~ 12 minutes
    print("Start time: ", datetime.now())
    #read in merged data created from data cleaner script
    df = pd.read_csv('dat/cleaned_df.csv')
    #copy result to be unscaled for roi testing.
    df['ResultClean'] = df['Result'].copy()

    
    fighters_list, divisions_list = create_fighters_and_divisions_list(df)
    fighters_stats_dict = {i: {} for i in fighters_list}
    
    
    
    fight_tally_dict, fight_tally_by_fight_id = create_fight_tally_dict(df, fighters_list)
    
    
    
    #create divisions stat means
    division_stat_dict = mean_stats_by_weight(df, divisions_list)
    
    
    #create previous weight class feature and create dictionary with rolling features
    df = create_previous_division_feature(df, fighters_list)
    

    print(datetime.now())
    
    #save dict of rolling stats
    with open('dat/fighters_rolling_stats.json', 'w') as outfile:
        json.dump(fighters_stats_dict, outfile)
    
    with open('dat/fighters_tally_stats.json', 'w') as outfile:
        json.dump(fight_tally_dict, outfile)
        
    with open('dat/fighters_tally_stats_by_fightid.json', 'w') as outfile:
        json.dump(fight_tally_by_fight_id, outfile)    
        
    with open('dat/division_mean_stats.json', 'w') as outfile:
        json.dump(division_stat_dict, outfile)