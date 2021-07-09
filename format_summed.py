

# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 16:30:21 2021

@author: KinzCode
"""

import pandas as pd
import numpy as np
import json
import sys


from copy import deepcopy 


from cols import fight_stat_cols, no_corner_fight_stat_cols, window_blue_red_hero_villain_col
from cols import window_hero_villain_col, summed_cols




        

def _map_rolling_means(row,  fighters_rolling_stats):
    """

    Parameters
    ----------
    row : a groupby funcion grouping by "FightID". Row will be a unique FightID and 1 row of data.
    fighters_rolling_stats : a dict containing all fighters within the dataset as keys,
                            holding dicts with FightID as the keys of all their fights, containing
                            the created rolling stat name as a key holding the value
                            
                            e.g. {'Conor McGregor' : {'4391' : {'Hero_Attempts' : 1345},
                                                              {'Hero_Landed' : 592}},
                                                    {'4840' : {'Hero_Attempts': 371},
                                                              {'Hero_Landed': 175}}
                                                                          }   

    Returns
    -------
    row : The origonal row with new columns created from the window_hero_villain_col list imported
        from cols.py, containing the corresponding piece of data taken from fighters_rolling_stats.

    """
    #reset index so easily able to access values within row
    row.reset_index(drop = True, inplace = True)
    #get fighter in red corner
    red = row['RedCorner'][0]
    #get fighter in blue corner
    blue = row['BlueCorner'][0]
    #obtain unique FightID
    fight_id = str(row['FightID'][0])
    #weight_class = str(row['WeightClass'][0])
    

    try:
        red_stats = fighters_rolling_stats[red][fight_id]
    except KeyError:
        red_stats = {}
    
    for col in window_hero_villain_col:
        try:
            stat = red_stats[col]
        except KeyError:
            stat = np.nan
        row[f'Red_{col}'] = stat
        
    try:
        blue_stats = fighters_rolling_stats[blue][fight_id]
    except KeyError:
        blue_stats = {}
   
    for col in window_hero_villain_col:
        try:
            stat = blue_stats[col]
        except KeyError:
            stat = np.nan
        row[f'Blue_{col}'] = stat
    

    return row

def apply_rolling_stats(df, fighters_rolling_stats):
    """
    Parameters
    ----------
    df : the cleaned df created from the data_cleaner.py script
    fighters_rolling_stats : a dict containing all fighters within the dataset as keys,
                            holding dicts with FightID as the keys of all their fights, containing
                            the created rolling stat name as a key holding the value
                            
                            e.g. {'Conor McGregor' : {'4391' : {'Hero_Attempts' : 1345},
                                                              {'Hero_Landed' : 592}},
                                                    {'4840' : {'Hero_Attempts': 371},
                                                              {'Hero_Landed': 175}}
                                                                          }                                                                      
    Returns
    -------
    df : TYPE
        DESCRIPTION.

    """
    
    df = pd.concat([df,pd.DataFrame(columns= window_blue_red_hero_villain_col)])
    df['FightID'] = df['FightID'].astype(int)
    df['FightID2'] = df['FightID']
    df = df.groupby('FightID2').apply(_map_rolling_means,  fighters_rolling_stats)
    df.reset_index(drop = True, inplace = True)
    return df


def drop_columns(df):
    """
    Parameters
    ----------
    df : takes in the formatted_df that has the new rolling variables mapped to it

    Returns
    -------
    df : formatted_df with only the created variables to feed the model.

    """
    df.reset_index(drop = True, inplace = True)
    model_cols = window_blue_red_hero_villain_col + ['ExperienceDifference'] + ['Result']
    df = df[model_cols]
    return df


def create_experience_difference(row):
    """
    Parameters
    ----------
    row : a groupby function grouping the formatted_df by FightID.

    Returns
    -------
    row : origonal row with new created variable column "ExperienceDifference" which is
        calculated by (RedCorner number of fights - BlueCorner number of fights) within 
        the dataset.

    """
    row.reset_index(drop = True, inplace = True)
    
    red = row['RedCorner'][0]
    blue = row['BlueCorner'][0]
    fight_id = str(row['FightID'][0])
    try:
        row['ExperienceDifference'] = (fighters_tally_stats_id[red][fight_id]) - (fighters_tally_stats_id[blue][fight_id])
    except KeyError:
        row['ExperienceDifference'] = np.nan
    return row

    
if __name__ == '__main__':
    with open('dat/fighters_rolling_stats.json') as json_file:
        fighters_rolling_stats = json.load(json_file)

    with open('dat/fighters_tally_stats.json') as json_file:
        fighters_tally_stats = json.load(json_file)
    
    with open('dat/fighters_tally_stats_by_fightid.json') as json_file:
        fighters_tally_stats_id = json.load(json_file)
        

    cleaned_df = pd.read_csv('dat/cleaned_df.csv')
    
    
    formatted_df = apply_rolling_stats(cleaned_df, fighters_rolling_stats)
    
    #fill nan values with column means
    formatted_df = formatted_df.fillna(formatted_df.mean())
    
    #add elo ratings and fight tallys
    formatted_df = formatted_df.groupby('FightID2').apply(create_experience_difference)
    #remove early fights
    formatted_df = formatted_df[(formatted_df['FightID'] > 4700)]
    
    # #drop unnecessary columns so model can be fitt
    formatted_df = drop_columns(formatted_df)
    
    formatted_df.to_csv('dat/formatted_df.csv', index = False)