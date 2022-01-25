# UFC_H2H_Predictions

## Contributors
Ben McKinnon & Daniel Braun

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Data sources](#data-sources)
* [Use](#use)

## General info
The purpose of this project is to make predictions on who is more likely to win a UFC bout and how likely each athlete is to win. This is achieved by sourcing historical data of athletes, and turning this into model features which can then be used to make such predictions. This model looks at how many strikes/submissions are attempted, landed, and control time a fighter has had over their opponents, as well as how many of these their opponents have had over them, across the athletes last 3 fights.

## Technologies
Project is created with:
  * Python 3.7.8
  * Pandas 1.0.3
  * Numpy 1.19.4
  * SKLearn 0.24.1

## Data sources
Included in this repository is data soured from "https://www.ufc.com/". The files and their contents are:
* *fighter_data.csv*: A record of 5000+ unique fights within the UFC, with a comprehensive record of the number of various strikes attempted, landed and ground control time had by each athlete within each fight.
* *fighter_results_dates.csv*: A record of the results of all fighters and the fights they fought, as well as the weight class and method of how they either won or lost.
* *event_date_location.csv*: A record of the Events and which country, city, and venue they were held at.

## Use
The project is divided into 5 separate scripts which need to run in the following order:
1. cols.py: Defines columns and creates column names to be used in creating features and tables, that are imported by later scripts.
2. data_cleaner.py: Cleans data by removing bad characters within the data and merges data sources into a single data frame. The returned data frame is saved to "dat/cleaned_df.csv".
3. feature_creator.py: Creates rolling model features and saves dictionaries as JSON files in the "dat" folder.
4. format_summed.py: Creates a data frame with the created features and target variable to train the model. Dataframe is saved as formatted_df.csv in the "dat" folder.
5. model.py: Predictions are made on a random set of fights using the SKLearn train, test, split method. A data frame is returned holding the predictions, fixture details, along with historical market data, so further analysis can be done on if the predictions can beat betting markets. The returned data frame is saved to "dat/testing_frame.csv"
