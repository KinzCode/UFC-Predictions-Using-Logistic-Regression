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


from cols import all_cols, fight_stat_cols, numerical_fight_stat_cols, no_corner_numerical_fight_stat_cols
from cols import hero_villain_corner_numerical_fight_stat_cols, red_blue_hero_villain_numerical_columns
from cols import window_blue_red_hero_villain_col, window_hero_villain_col


def _get_means(row, colour_corner_fighter, fight_id, weight_class, colour_of_corner,  fighters_rolling_stats, division_mean_stats):
    
    try:
        stats = fighters_rolling_stats[colour_corner_fighter][fight_id]
        for col in window_hero_villain_col:
            stat = stats[col]
 
            if stat == np.nan or stat == None:
                row[f'{colour_of_corner}_{col}'] = division_mean_stats[weight_class][col]
            else:
                row[f'{colour_of_corner}_{col}'] = stat

             
                    
    except KeyError:
        for col in window_hero_villain_col:
            origonal_col = col
            col = col.replace("Hero_", "").replace("Villain_", "").replace("_window_1", "").replace("_window_2", "").replace("_window_3", "")
    
            try:
                mean_suplimentary_value = division_mean_stats[weight_class][col]
            except KeyError:
                mean_suplimentary_value = (cleaned_df[f'Red_{col}'] + cleaned_df[f'Blue_{col}']).mean()
            
            row[f'{colour_of_corner}_{col}'] = mean_suplimentary_value
        

def _map_rolling_means(row,  fighters_rolling_stats, division_mean_stats):
    #row = deepcopy(row)
    row.reset_index(drop = True, inplace = True)
    red = row['RedCorner'][0]
    blue = row['BlueCorner'][0]
    fight_id = str(row['FightID'][0])
    weight_class = str(row['WeightClass'][0])
    
    
    # row = _get_means(row, red, fight_id, weight_class, 'Red',  fighters_rolling_stats, division_mean_stats)
    # row = _get_means(row, blue, fight_id, weight_class, 'Blue',  fighters_rolling_stats, division_mean_stats)

    try:
        red_stats = fighters_rolling_stats[red][fight_id]
        for col in window_hero_villain_col:
            stat = red_stats[col]
            row[f'Red_{col}'] = stat
            # if stat > 0:
            #     row[f'Red_{col}'] = stat
            # else:
            #     row[f'Red_{col}'] = (cleaned_df[f'Red_{col}'] + cleaned_df[f'Blue_{col}']).mean()
    except KeyError:
        for col in window_hero_villain_col:
            orig_col = col
            col = col.replace("Hero_", "").replace("Villain_", "").replace("_window_1", "").replace("_window_2", "").replace("_window_3", "")
            try:
                mean_suplimentary_value = division_mean_stats[weight_class][col]
            except KeyError:
                mean_suplimentary_value = (cleaned_df[f'Red_{col}'] + cleaned_df[f'Blue_{col}']).mean()
              
   
                
            row[f'Red_{orig_col}'] = mean_suplimentary_value   


                                                     
    try:
        blue_stats = fighters_rolling_stats[blue][fight_id]
        for col in window_hero_villain_col:
            stat = blue_stats[col]
            row[f'Blue_{col}'] = stat
            # if stat > 0:
                
            # else:
            #     row[f'Blue_{col}'] = (cleaned_df[f'Red_{col}'] + cleaned_df[f'Blue_{col}']).mean()
                
    except KeyError:
        for col in window_hero_villain_col:
            orig_col = col
            col = col.replace("Hero_", "").replace("Villain_", "").replace("_window_1", "").replace("_window_2", "").replace("_window_3", "")
            try:
                mean_suplimentary_value = division_mean_stats[weight_class][col]
            except KeyError:
                mean_suplimentary_value = (cleaned_df[f'Red_{col}'] + cleaned_df[f'Blue_{col}']).mean()
              
            row[f'Blue_{orig_col}'] = mean_suplimentary_value
    
    return row
    
    

def apply_rolling_stats(df, fighters_rolling_stats, division_mean_stats):
    """ 
    
    """
    
    df = pd.concat([df,pd.DataFrame(columns= window_blue_red_hero_villain_col)])
    df['FightID'] = df['FightID'].astype(int)
    df['FightID2'] = df['FightID']
    df = df.groupby('FightID2').apply(_map_rolling_means,  fighters_rolling_stats, division_mean_stats)
    return df


def drop_columns(df):
    df.reset_index(drop = True, inplace = True)
    model_cols = window_blue_red_hero_villain_col + ['Result']
    df = df[model_cols]
    return df


if __name__ == '__main__':
    with open('dat/fighters_rolling_stats.json') as json_file:
        fighters_rolling_stats = json.load(json_file)

    with open('dat/fighters_tally_stats.json') as json_file:
        fighters_tally_stats = json.load(json_file)
        
    with open('dat/division_mean_stats.json') as json_file:
        division_mean_stats = json.load(json_file)
        
    
    
    cleaned_df = pd.read_csv('dat/cleaned_df.csv')
    #cleaned_df = df.to_csv('dat/fortmatted_df.csv')
    
    formatted_df = apply_rolling_stats(cleaned_df, fighters_rolling_stats, division_mean_stats)
    
    #drop unnecessary columns so model can be fitt
    formatted_df = drop_columns(formatted_df)
    
    formatted_df.to_csv('dat/formatted_df.csv', index = False)