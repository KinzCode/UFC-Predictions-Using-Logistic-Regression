# UFC_H2H_Predictions

## Contributors
Ben McKinnon & Daniel Braun

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Data sources](#data-sources)
* [Use](#use)

## General info
The purpose of this project is to make predictions on who is more likely to win a UFC bout and how likely each athlete is to win. This is achieved by sourcing historical data of athletes, and turning this into model features which can then be used to make such predictions. This model looks at how many strikes/submissions are attempted, landed , and control time a fighter has had over their opponents, as well as how many of these their opponents have had over them, across the athletes last 3 fights.

## Technologies
Project is created with:
* Python 3.7.8
  * Pandas 1.0.3
  * Numpy 1.19.4
  * SKLearn 0.24.1

## Data sources
Included in this repositroy is 3 separate csv files which were scraped directly from https://www.ufc.com/. The files and their contents are:
* *fighter_data.csv*: A record of 5000+ unique fights within the UFC, with a comprehensive record of the number of various strikes attempted, landed and ground control time had by each athlete within each fight.
* *fighter_results_dates.csv*: A record of the results of all fighters and the fights they fought, as well as the weightclass and method of how they either won or lost.
* *event_date_location.csv*: A record of the Events and which country, city and venue they were held at.

## Use
The projects is divided into 5 separate scripts which need to be ran in the following order:
1. cols.py
2. data_cleaner.py
3. feature_creator.py
4. format_summed.py
5. model.py
