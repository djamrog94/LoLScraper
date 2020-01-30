import pandas as pd
import numpy as np
from datetime import datetime
from riotwatcher import RiotWatcher, ApiError
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
api_key = 'RGAPI-3b3cf6a1-945c-4b26-ad43-cc51b96ff21a'

watcher = RiotWatcher(api_key)


df = pd.read_excel('master_file.xlsx')
df.fillna(0, inplace=True)

team_data = df.loc[df['player'] == 'Team']
X = team_data.iloc[:, 20:98]
cols = df.columns[20:98]
X[cols] = X[cols].apply(pd.to_numeric, errors='coerce')
X = X[['fb', 'ft', 'fd', 'gdat10', 'csdat10']]

X = X.fillna(0)
y = team_data.iloc[:, -1]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


clf = LogisticRegression(solver='liblinear', random_state=0).fit(X_train, y_train)
print(f'score: {clf.score(X_test, y_test)}')
prediction = np.array([0, 0, 1, 600, 2])
prediction = prediction.reshape(1,-1)
predicted = clf.predict(prediction)
print(f'predicted: {predicted}')


# def get_game():
#     """
#     :return: two strings of the two teams that are playing next
#     """
#     schedule = pd.read_csv('LCS_2020_Spring_Schedule.csv')
#     schedule['Date'] = pd.to_datetime(schedule['Date'])
#     for n in range(len(schedule)):
#         if datetime.now() < schedule.iloc[n]['Date']:
#             teams = schedule.iloc[n]['Subject'].split('-')[1].lstrip()
#             return teams.split(' vs ')
#         elif range(len(schedule)) == 0:
#             teams = schedule.iloc[n]['Subject'].split('-')[1].lstrip()
#             return teams.split(' vs ')
#
#
# def get_players():
#     team1, team2 = get_game()
#     payload = pd.read_excel('lol_rosters.xlsx')
#     rosters = {}
#     roster = []
#     for team in [team1, team2]:
#         payload = payload.loc[payload['Abbrev'] == team]
#         for i in range(len(payload)):
#             roster.append([payload.iloc[i]['Name'], payload.iloc[i]['Role']])
#         rosters[team] = roster
#     return rosters
#
#
# def get_summoner_id(summoner_name):
#     me = watcher.summoner.by_name('NA1', 'Huni')
#     return me['id']
#
#
# def get_live():
#     rosters = get_players()
#     blue_team, read_team = rosters.keys()
#     summoner_id = get_summoner_id(rosters[blue_team][0][0])
#     game = watcher.spectator.by_summoner('NA1', summoner_id)
#     print(game)
#
#
# get_live()