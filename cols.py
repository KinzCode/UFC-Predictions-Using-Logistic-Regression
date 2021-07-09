# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 17:00:47 2021

@author: KinzCode
"""

import pandas as pd


def create_fight_stat_cols(df):
    """
    Parameters
    ----------
    df : Base df with all fights stats/data.

    Returns
    -------
    fight_stat_cols : List of all columns that are stats from fights.

    """
    good_words = ['Attempts', 'Landed', 'Time']
    df_cols = df.columns
    fight_stat_cols = [i for i in df_cols if any(x in i for x in good_words)]
    #remove fight end time as its not a metric of athlete individual performance
    fight_stat_cols.remove("FightEndTime")
    return fight_stat_cols

def create_no_corner_fight_stat_cols(fight_stat_cols):
    """
    Parameters
    ----------
    fight_stat_cols : List of all columns that are stats from fights.

    Returns
    -------
    no_corner_fight_stat_cols : List of all unique columns that are stats from fights,
                                withe the corner removed.

    """
    #take just the red corner stats as columns are identical for both red and blue
    fight_stat_cols = [i for i in fight_stat_cols if 'Red' in i]
    no_corner_fight_stat_cols = [x.replace('Red_', "") for x in fight_stat_cols]
    return no_corner_fight_stat_cols
    
def create_window_blue_red_hero_villain_col(summed_cols):
    """
    Parameters
    ----------
    summed_cols : Defined column headings that represent the sum of respective columns.
    Returns
    -------
    window_blue_red_hero_villain_col : A list of columnn names for created model features.

    """
    window_blue_red_hero_villain_col = []

    for colour in ['Red_', 'Blue_']:
        for col in summed_cols:
            for string in ['_window_1', '_window_2', '_window_3']:
                new_col = colour + col + string
                window_blue_red_hero_villain_col.append(new_col)
    
    return window_blue_red_hero_villain_col
    

def create_window_hero_villain_col(summed_cols):
    """
    Parameters
    ----------
    summed_cols : Defined column headings that represent the sum of respective columns.

    Returns
    -------
    window_hero_villain_col : A list of columnn names for created model features without corner
                            identification

    """
    window_hero_villain_col = []

    for col in summed_cols:
        for string in ['_window_1', '_window_2', '_window_3']:
            new_col = col + string
            window_hero_villain_col.append(new_col)      
    
    return window_hero_villain_col


def run():
    """
    Runs script and returns defined column lists to be used within the project.
    """
    df = pd.read_csv('dat/fighter_data.csv')
    
    #define columns
    colour_summed_cols = [
                        'Red_Hero_Attempts',
                        'Red_Hero_Landed',
                        'Red_Villain_Attempts',
                        'Red_Villain_Landed',
                        'Blue_Hero_Attempts',
                        'Blue_Hero_Landed',
                        'Blue_Villain_Attempts',
                        'Blue_Villain_Landed',
                        ]
     
    summed_cols = [
                'Hero_Attempts',
                'Hero_Landed',
                'Hero_Time',
                'Villain_Attempts',
                'Villain_Landed',
                'Villain_Time'
                ]
    
    fight_stat_cols = create_fight_stat_cols(df)
    no_corner_fight_stat_cols = create_no_corner_fight_stat_cols(fight_stat_cols)
    window_hero_villain_col = create_window_hero_villain_col(summed_cols)
    window_blue_red_hero_villain_col = create_window_blue_red_hero_villain_col(summed_cols)
    
    return fight_stat_cols, no_corner_fight_stat_cols, window_hero_villain_col, window_blue_red_hero_villain_col




fight_stat_cols, no_corner_fight_stat_cols, window_hero_villain_col, window_blue_red_hero_villain_col = run()
