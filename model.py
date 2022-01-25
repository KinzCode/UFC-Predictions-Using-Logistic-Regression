# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 09:55:15 2021

@author: KinzCode
"""

import pandas as pd
import numpy as np


from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error




def fit_model(df):
    """
    Parameters
    ----------
    df : Takes in formatted_df which was compiled in format_summed.py. Each
        row is a unique fight with the rolling stats for the fighter in the
        red corner and for that in the blue corner.
    
    Returns
    -------
    y_pred : the predicted probabilty for RedCorner to win.
    index : the index values for the random sample of y_pred.
    
    Additional
    ---------
    Target variable is "Result" which is a binary 1 or 0 value which represnts win (1) or loss (0).
    """
    
    #map result to binary
    df['Result'] = df['Result'].map({'Win': 1, 'Loss': 0})
    #feature cols are all columns not our targer ('Result')
    feature_cols = [i for i in df.columns if 'Result'  not in i]
    X = df[feature_cols]
    
    
    # Normalize X data
    min_max_scaler = preprocessing.MinMaxScaler()
    X = min_max_scaler.fit_transform(X)
    #define target y variabl
    y = df['Result']
    
    #randomly train test split data
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.5,random_state=0)
    
    # instantiate the model (using the default parameters)
    logreg = LogisticRegression() #'#, max_iter=10000)
    
    # fit the model with data
    logreg.fit(X_train,y_train)
    
    print(logreg)
    
    #pred
    y_pred= logreg.predict_proba(X_test)

    
    mae = mean_absolute_error(y_test, y_pred[:,0])
    mse = mean_squared_error(y_test, y_pred[:,0])
    print("MAE for this model is: ", mae)
    print("MSE for this model is: ", mse)

    #convert scaled aray back to df
    X_test = pd.DataFrame(X_test, columns = feature_cols)
    
    #get index of test rows
    index = list(y_test.index.values)
    
    return y_pred, index
 

   
def create_test_preds(df, preds, index):
    """
    Parameters
    ----------
    df : takes in cleaned_df which holds fixture and odds information.
    preds : the predicted Y values returned from fit_model function.
    index : the index list of the predicted values.

    Returns
    -------
    df : A dataframe containing our predictions and the corresponding fixture information
        as well as historical odds data to backtest and see if the predictions can beat pinnacle 
        closing line.

    """
    
    df = df.loc[index]
    preds = preds[:,0]
    df['Pred'] = preds
    
    result_dict = {'Win': 1, 'Loss': 0}
    df['Result'] = df['Result'].map(result_dict)
    df['ResultClean'] = df['Result']
    
    return df
    
if __name__ == '__main__':
    df = pd.read_csv('dat/formatted_df.csv') 
    df.dropna(inplace = True)
    clean_df = pd.read_csv('dat/cleaned_df.csv')
    
    
    preds, index = fit_model(df)
    
    test_preds_frame = create_test_preds(clean_df, preds, index)
    
    test_preds_frame.to_csv('dat/testing_frame.csv', index = False)