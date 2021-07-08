# UFC_H2H_Predictions

## Contributors
Ben McKinnon & Daniel Braun

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Data sources](#data-sources)
* [Use](#use)

## General info
Predicting who will win and lose a fight in the UFC based on their hisotrical performances using logistic regression.
	
## Technologies
Project is created with:
* Python 3.7.8
  * Pandas 1.0.3
  * Numpy 1.19.4
  * SKLearn 0.24.1

## Data sources
Included in this repositroy is 3 separate csv files which were scraped directly from https://www.ufc.com/. The files and their contents are:
* fighter_data.csv: A record of 5000+ unique fights within the UFC, with a comprehensive record of the number of various strikes attempted, landed and ground control time had by each athlete within each fight.
* fighter_results_dates.csv: A record of the results of all fighters and the fights they fought, as well as the weightclass and method of how they either won or lost.
* event_date_location.csv: 

## Use
The projects is divided into 5 separate scripts which need to be ran in the following order:
1. cols.py
2. data_cleaner.py
3. feature_creator.py
4. format_summed.py
5. model.py
