#🏏 **CRICKET SCORE PREDICTOR USING ML 🏏**


# Import Libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the Datasets

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

balls_path = os.path.join(BASE_DIR, "datasets", "IPL_Ball_by_Ball_2008_2022.csv")
matches_path = os.path.join(BASE_DIR, "datasets", "IPL_Matches_2008_2022.csv")

balls = pd.read_csv(balls_path)
matches = pd.read_csv(matches_path)


# Match Dataset

print(matches.head())
print("\n------------------------------------------\n")
print(matches.shape)
print("\n------------------------------------------\n")
print(matches.columns)

# Ball Dataset

print(balls.head())
print("\n------------------------------------------\n")
print(balls.shape)
print("\n------------------------------------------\n")
print(balls.columns)

# Check Missing Values

print(matches.isnull().sum())
print(balls.isnull().sum())

# Keep Only First Innings

balls = balls[balls['innings'] == 1]

# Calculate Current Score

balls['current_score'] = balls.groupby('ID')['total_run'].cumsum()
balls[['ID','overs','ballnumber','current_score']].head(20)

# Calculate Wickets Lost

balls['isWicketDelivery'] = balls['isWicketDelivery'].fillna(0)
balls['wickets'] = balls.groupby('ID')['isWicketDelivery'].cumsum()
balls[['current_score','wickets']].head(20)

# Create Current Over

balls['current_over'] = balls['overs'] + balls['ballnumber']/10
balls[['ballnumber' , 'current_over']].head(12)

# Calculate Run Rate

balls['current_rr'] = (balls['current_score'] / balls['current_over'])
balls[['current_over' , 'current_rr']].head(20)

# Final Scores

final_scores = balls.groupby('ID')['current_score'].max().reset_index()
final_scores.rename(columns = {'current_score' : 'final_score'} , inplace = True)
final_scores.head()

# Merge Final Scores

df = balls.merge(final_scores , on = 'ID')
df.head(10)

# Venue Information

match_info = matches[['ID','Venue','Team1','Team2']]
df = df.merge(match_info , on = 'ID')
df.head()

# Balls Remaining

balls_played = (df['overs'] * 6 + df['ballnumber'])
df['balls_left'] = 120 - balls_played
df[['current_over' , 'balls_left']].head()

# Wickets Left

df['wickets_left'] = 10 - df['wickets']
df[['wickets','wickets_left']].head()
df['tail_end'] = np.where(
    df['wickets_left'] <= 1,
    1,
    0
)
df[['wickets_left', 'tail_end']].head()
df['balls_per_wicket'] = (
    df['balls_left'] /
    (df['wickets_left'] + 1)
)
df[['balls_left', 'wickets_left', 'balls_per_wicket']].head()
df['death_risk'] = np.where(
    (df['wickets_left'] <= 2) &
    (df['balls_left'] >= 24),
    1,
    0
)
df[['wickets_left', 'balls_left', 'death_risk']].head()

# Runs in Last 5 Overs

df['last_5_runs'] = (
    df.groupby('ID')['total_run']
      .rolling(30, min_periods=1)
      .sum()
      .reset_index(level=0, drop=True)
)
df[['current_score','last_5_runs']].head(40)

# Wickets in Last 5 Overs

df['last_5_wickets'] = (
    df.groupby('ID')['isWicketDelivery']
      .rolling(30, min_periods=1)
      .sum()
      .reset_index(level=0, drop=True)
)
df[['wickets','last_5_wickets']].head(40)

# Phase

def get_phase(over):

    if over <= 6:
        return 'Powerplay'

    elif over <= 15:
        return 'Middle Overs'

    else:
        return 'Death Overs'

df['phase'] = df['current_over'].apply(get_phase)
df[['current_over','phase']].head(120)

# Create Bowling Team

df['BowlingTeam'] = np.where(
    df['BattingTeam'] == df['Team1'],
    df['Team2'],
    df['Team1']
)
df[['BattingTeam','BowlingTeam']].head()

# Venue Average Score

venue_avg = (
    df.groupby('Venue')['final_score']
      .mean()
)
df['venue_avg'] = df['Venue'].map(venue_avg)
df[['Venue','venue_avg']].head()

# Runs Left

df['runs_left'] = (df['final_score'] - df['current_score'])
df[['current_score' , 'runs_left']].head()

# Remove Invalid Rows

df = df[df['balls_left'] >= 0]
df = df[df['runs_left'] >= 0]

# Select Features

final_df = df[[
    'Venue',
    'BattingTeam',
    'BowlingTeam',
    'current_over',
    'current_score',
    'extras_run',
    'wickets_left',
    'current_rr',
    'balls_left',
    'last_5_runs',
    'last_5_wickets',
    'phase',
    'venue_avg',
    'tail_end',
    'balls_per_wicket',
    'death_risk',
    'final_score'
]]
final_df.head()

# Remove Initial Overs

final_df = final_df[final_df['current_over'] >= 6]
final_df.head()

# Encode Categorical Variables

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

# Define X and y

X = final_df.drop('final_score', axis=1)
y = final_df['final_score']

# Train Test Split

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Preprocessing Pipeline

trf = ColumnTransformer(
[
    (
        'ohe',
        OneHotEncoder(handle_unknown='ignore'),
        [
            'Venue',
            'BattingTeam',
            'BowlingTeam',
            'phase'
        ]
    )
],
remainder='passthrough'
)

# Random Forest

from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
pipe_rf = Pipeline(
[
    ('transformer', trf),

    ('model',
     RandomForestRegressor(
         n_estimators=50,
         max_depth=20,
         min_samples_leaf=3,
         random_state=42,
         n_jobs=-1
     ))
]
)
pipe_rf.fit(X_train, y_train)

# Prediction

pred_rf = pipe_rf.predict(X_test)

# Evaluation

from sklearn.metrics import *
print("MAE :", mean_absolute_error(y_test, pred_rf))
print("RMSE :", np.sqrt(mean_squared_error(y_test, pred_rf)))
print("R2 Score :", r2_score(y_test, pred_rf))

# Save Model

import joblib
joblib.dump(pipe_rf , "cricket_model.pkl")

# # Predicting Live Score

# # ============================
# # 🏏 IPL LIVE SCORE PREDICTOR
# # ============================

# import pandas as pd
# import numpy as np

# print("="*65)
# print("🏏             IPL LIVE SCORE PREDICTOR             🏏")
# print("="*65)

# # USER INPUTS

# venue = input("📍 Enter Venue                     :    ")
# batting_team = input("🏏 Enter Batting Team              :    ")
# bowling_team = input("🎯 Enter Bowling Team              :    ")
# current_over = float(input("⏱️ Enter Overs Played              :    "))
# current_score = int(input("🔢 Enter Current Score             :    "))
# extras_run = int(input("➕ Enter Extras Runs               :    "))
# wickets = int(input("❌ Enter Wickets Lost              :    "))
# last_5_runs = int(input("🔥 Runs in Last 5 Overs            :    "))
# last_5_wickets = int(input("💥 Wickets Lost in Last 5 Overs    :    "))

# # CALCULATIONS

# whole_over = int(current_over)
# balls = round((current_over - whole_over) * 10)

# balls_played = whole_over * 6 + balls
# balls_left = 120 - balls_played

# wickets_left = 10 - wickets

# if current_over > 0:
#     current_rr = current_score / current_over
# else:
#     current_rr = 0

# # Innings Phase

# if current_over <= 6:
#     phase = "Powerplay"
# elif current_over <= 15:
#     phase = "Middle"
# else:
#     phase = "Death"

# # Venue Average

# venue_avg = final_df[
#     final_df['Venue'] == venue
# ]['final_score'].mean()

# if np.isnan(venue_avg):
#     venue_avg = final_df['final_score'].mean()

# # Tail-End Situation

# if wickets_left <= 1:
#     tail_end = 1
# else:
#     tail_end = 0

# # Balls Per Wicket

# balls_per_wicket = balls_left / (wickets_left + 1)

# # Death Risk

# if wickets_left <= 2 and balls_left >= 24:
#     death_risk = 1
# else:
#     death_risk = 0

# # VALID INPUTS

# if (
#     0 <= wickets < 10 and
#     0 < current_over <= 20 and
#     extras_run >= 0 and
#     current_score >= 0 and
#     balls_left >= 0 and
#     0 <= last_5_wickets <= 5 and
#     last_5_runs >= 0
# ):

#     sample = pd.DataFrame({
#         'Venue': [venue],
#         'BattingTeam': [batting_team],
#         'BowlingTeam': [bowling_team],
#         'current_over': [current_over],
#         'current_score': [current_score],
#         'extras_run': [extras_run],
#         'wickets_left': [wickets_left],
#         'current_rr': [current_rr],
#         'balls_left': [balls_left],
#         'last_5_runs': [last_5_runs],
#         'last_5_wickets': [last_5_wickets],
#         'phase': [phase],
#         'venue_avg': [venue_avg],
#         'tail_end': [tail_end],
#         'balls_per_wicket': [balls_per_wicket],
#         'death_risk': [death_risk]
#     })

#     prediction = pipe_rf.predict(sample)

#     pred = int(prediction[0])

#     # Cricket Logic Corrections

#     if wickets_left == 1:
#         pred = min(pred, current_score + 20)

#     elif wickets_left == 2:
#         pred = min(pred, current_score + 35)

#     pred = max(pred, current_score)

#     lower = pred - 5
#     upper = pred + 5

#     # MATCH SUMMARY

#     print("\n" + "="*65)
#     print("📊                 MATCH SUMMARY")
#     print("="*65)

#     print(f"🏟️ Venue                          :    {venue}")
#     print(f"🏏 Batting Team                   :    {batting_team}")
#     print(f"🎯 Bowling Team                   :    {bowling_team}")
#     print(f"🔢 Current Score                  :    {current_score}/{wickets}")
#     print(f"⏱️ Overs Played                   :    {current_over}")
#     print(f"📈 Current Run Rate               :    {current_rr:.2f}")
#     print(f"🎯 Balls Left                     :    {balls_left}")
#     print(f"🧤 Wickets Left                   :    {wickets_left}")
#     print(f"🔥 Runs in Last 5 Overs           :    {last_5_runs}")
#     print(f"💥 Wickets in Last 5 Overs        :    {last_5_wickets}")
#     print(f"⚡ Innings Phase                  :    {phase}")
#     print(f"🏟️ Venue Average Score            :    {venue_avg:.0f}")

#     print("="*65)
#     print("🧠              ADVANCED ANALYTICS")
#     print("="*65)

#     print(f"🏁 Tail-End Situation             :    {'Yes' if tail_end == 1 else 'No'}")
#     print(f"⚠️ Death Risk                     :    {'High' if death_risk == 1 else 'Normal'}")
#     print(f"📊 Balls per Wicket               :    {balls_per_wicket:.2f}")

#     print("="*65)
#     print(f"🤖 Predicted Final Score          :    {pred} Runs")
#     print(f"📌 Predicted Score Range          :    {lower} - {upper} Runs")
#     print("="*65)
#     print("✅ Prediction Generated Successfully!")
#     print("="*65)

#     if pred >= 200:
#         status = "🔥 Explosive Innings Expected"
#     elif pred >= 170:
#         status = "💪 Competitive Total Expected"
#     elif pred >= 150:
#         status = "⚡ Average Total Expected"
#     else:
#         status = "💔 Below Par Score Expected"

#     print(f"🏆 Match Insight                  :    {status}")
#     print("="*65)

# # ALL OUT CASE

# elif (
#     wickets == 10 and
#     0 < current_over <= 20 and
#     extras_run >= 0
# ):

#     print("\n" + "="*65)
#     print("🏏                 INNINGS OVER")
#     print("="*65)

#     print(f"🏏 Team                           :    {batting_team}")
#     print(f"🎯 Against                        :    {bowling_team}")
#     print(f"🔢 Final Score                    :    {current_score} ALL OUT")
#     print(f"⏱️ Overs Played                   :    {current_over}")

#     print("="*65)

#     if current_score >= 200:
#         status = "🔥 Explosive Innings"
#     elif current_score >= 170:
#         status = "💪 Competitive Total"
#     elif current_score >= 150:
#         status = "⚡ Average Total"
#     else:
#         status = "💔 Below Par Score"

#     print(f"🏆 Match Insight                  :    {status}")
#     print("="*65)

# # INVALID INFORMATION

# else:

#     print("\n" + "="*65)
#     print("❌            INVALID MATCH INPUT REPORT")
#     print("="*65)

#     if wickets < 0 or wickets > 10:
#         print(f"🚫 Invalid Wickets Entered           :    {wickets}")
#         print("💡 Wickets must be between 0 and 10.\n")

#     if current_over <= 0 or current_over > 20:
#         print(f"🚫 Invalid Overs Entered             :    {current_over}")
#         print("💡 Overs must be between 0.1 and 20.0.\n")

#     if extras_run < 0:
#         print(f"🚫 Invalid Extras Entered            :    {extras_run}")
#         print("💡 Extras cannot be negative.\n")

#     if current_score < 0:
#         print(f"🚫 Invalid Score Entered             :    {current_score}")
#         print("💡 Score cannot be negative.\n")

#     if last_5_runs < 0:
#         print(f"🚫 Invalid Last 5 Overs Runs         :    {last_5_runs}")
#         print("💡 Runs cannot be negative.\n")

#     if last_5_wickets < 0 or last_5_wickets > 5:
#         print(f"🚫 Invalid Last 5 Wickets            :    {last_5_wickets}")
#         print("💡 Wickets must be between 0 and 5.\n")

#     print("="*65)
#     print("⚠️ Please enter valid cricket match information.")
#     print("🔄 Restart the predictor and try again.")
#     print("="*65)