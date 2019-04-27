# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 08:04:40 2019

@author: chuck
"""
import numpy as np
import pandas as pd

#***************************************************************************************************

# this function reads dataset and returns df for given date range 
def results_1(begin, end):
    df = pd.read_csv(r'results.csv', parse_dates=[0])   
    df = df[df['date'] >= begin]
    df = df[df['date'] <= end]
    return df


def conv_tournament(S):
    L = set(S.unique())
    A = {'FIFA World Cup'}
    B = {'AFC Asian Cup', 'African Cup of Nations', 'Copa América', 'Gold Cup', 'Nations Cup',
         'Copa América', 'UEFA Euro'}
    C = {'FIFA World Cup qualification', 'AFC Asian Cup qualification', 'African Cup of Nations qualification',
        'Copa América qualification', 'Gold Cup qualification', 'CONCACAF Championship', 'UEFA Euro qualification'}
    E = {'Friendly'}
    D = L - A - B - C - E
    return  {60:A, 50:B, 40:C, 30:D, 20:E}


def set_k(S, dict):
    A = []
    for s in S:
        for key, val in dict.items():
            if s in val:
                A.append(key)
    return A


def result(gdf):
    if not gdf:         return 0.50
    if gdf == abs(gdf): return 1.00
    else:               return 0.00

    
def results_2(df):   
    df.columns = ['date', 'home', 'away', 'home_score', 'away_score', 'tournament', 'city', 'country', 'neutral']  
    df['gdf']      = np.subtract(df.home_score, df.away_score)
    df['draw']     = np.where(df['gdf'] == 0, True, False)
    df['win']      = np.where(df.gdf > 0, True, False)
    df['k']        = set_k(df.tournament, conv_tournament(df.tournament)) 
    df['result']   = df.gdf.apply(lambda x : result(x))  
    df['gdf']      = df.gdf.abs()
    df = df.drop(['home_score', 'away_score', 'city', 'country', 'tournament'], axis=1)    
    return df


# this function calculates G value 
def calc_g(gdf):    # gdf is int >= 0
    if not gdf:  return 1.00
    if gdf == 1: return 1.00
    if gdf == 2: return  1.50 
    else:        return (11 + gdf) / 8  

# calculates p(win) based upon the differnce in ratings 
def win_exp(dfr):                            # dfr is home rating - away rating 
    return 1 / ((10) ** (-dfr / 400) + 1)   # actually home win prob.  away is (1.00 - win_exp(dfr))

# the results df with all countries rating at "begin" date
def start_results(date,dict):
    A = []
    for key, val in dict.items():
        S = pd.Series([date, key, int(val)])
        A.append(S)
    df = pd.DataFrame(A)
    df.columns = ['date', 'country', 'rating']
    return df

#creates ratings dict to begin an analysis for initial time period
def teams_rate_begin(df):
    all = set(df.home.unique()) | set(df.away.unique())
    rtgs = {}
    for team in all:
        rtgs[team] = 1500   
    return rtgs

def teams_rate_next(df, dict):
    all_team = set(df.home.unique()) | set(df.away.unique())
    add_team = all_team - set(dict.keys())
    for team in add_team:
        rtgs[team] = 1500   
    return rtgs

    