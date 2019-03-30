# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 08:04:40 2019

@author: chuck
"""
import numpy as np
import pandas as pd

def results_1():   
    return pd.read_csv(r'results.csv', parse_dates=[0])

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

# this function prepares intial data frame 
def results_2(df):   
    df.columns = ['date', 'home', 'away', 'home_score', 'away_score', 'tournament', 'city', 'country', 'neutral']
    df['gdf'] = np.subtract(df.home_score, df.away_score)
    df['draw']     =  np.repeat(True,len(df))
    df['draw']     = df.draw.where(df.gdf == 0, other=False)
    df['home_win'] = np.repeat(True,len(df))
    df['home_win'] = df.home_win.where(df.gdf > 0, other=False)
    df['gdf']      = df.gdf.abs()
    
    df['k']        = set_k(df.tournament, conv_tournament(df.tournament)) 
    
    df = df.drop(['home_score', 'away_score', 'city', 'country', 'tournament'], axis=1)  
    
    return df

# creates dictionary of all teams in df, 1400 is default rating

def teams_rate_begin(df):
    all = set(df.home.unique()) | set(df.away.unique())
    rtgs = {}
    for team in all:
        rtgs[team] = 1400   
    return rtgs

def win_exp(dfr):
    return 1 / ((10) ** (-dfr / 400) + 1)

# k is then adjusted for the goal difference in the game. It is increased by half if a game is won by two goals,
# by 3/4 if a game is won by three goals, and by 3/4 + (N-3)/8 if the game is won by four or more goals,
# where N is the goal difference

def calc_g(gdf):    # gdf is int >= 0
    if not gdf:  return 0.50
    if gdf == 1: return 1.00
    if gdf == 2: return  1.50 
    else:        return (11 + gdf) / 8 

#creates data frame with one row of country current ratings plus date
def ratings_df(dict):
    S = pd.Series(dict)  
    return pd.DataFrame({df.iat[0,0]:S})


  
df = results_1() 
df = results_2(df)
#  ********* main ********************************
#  0     1    2      3        4    5       6      7        
# date  home  away  nuetral  gdf  draw  home_win  k

rtgs = teams_rate_begin(df)
df_rtgs = ratings_df(rtgs)

for (row, S) in df.iterrows():
    win_probs =[]
    
    home, away = S[1], S[2]                             # strings
    nuetral, draw, win, favor = S[3], S[5], S[6], True  # bools
    gdf, k =  S[4], S[7]                                # ints 
    
    home_rtg, away_rtg = rtgs[home], rtgs[away]
    if not nuetral:   dfr = home_rtg + 100 - away_rtg                    # not nuetral? ==> home rating + 100                                    
    else:    dfr = home_rtg - away_rtg
    if dfr < 0: favor = False
        
    expect = win_exp(dfr)
    adjust = np.round(calc_g(gdf) * k * (1.0 - expect), decimals=0)  
    
    if win or draw and not favor:                     # if home team wins or draws when not favored, rating increases
        home_rtg += adjust
        away_rtg -= adjust
    else:
        home_rtg -= adjust
        away_rtg += adjust 
        
    if win: win_probs.append(expect)                            # appends list with winning team's P(expect)
    else:   win_probs.append(1.0 - expect)
    
    df_rtgs[S[0]] = pd.Series({S[1]:home_rtg, S[2]:away_rtg})      # new column in ratings dataframe 
    
    rtgs[S[1]] = home_rtg; rtgs[S[2]] = away_rtg                # update current ratings 
    