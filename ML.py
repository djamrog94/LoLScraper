import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import datetime
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import sklearn

# required machine learning packages
from sklearn import model_selection
from sklearn.feature_selection import RFE
from sklearn.metrics import brier_score_loss, roc_auc_score, accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV as CCV

from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, VotingClassifier
import xgboost as xgb




Points = {
    'Top': 20,
    'Jungle': 15,
    'Middle': 22,
    'ADC': 22,
    'Support': 12,
    'Team': 20
}


# def line(r):
#     if r['points'] > Points[r['position']]:
#         return True
#     else:
#         return False
#
#
# def reassemble(r):
#     if r['playerid'] in range(1, 6):
#         pass
#     elif r['playerid'] in range(6, 11):
#         pass
#     elif r['playerid'] == 100:
#         pass
#     else:
#         pass
#
df = pd.read_excel('master_file.xlsx')
df.fillna(0, inplace=True)
# game_id = []
# for i in range(len(df)):
#     if df.iloc[i]['gameid'] not in game_id:
#         game_id.append(df.iloc[i]['gameid'])
#
# train_id = []
# for _ in range(int(len(game_id) * .8)):
#     train_id.append(game_id.pop(random.randint(0, len(game_id))))
#
# train_result = []
# for i in range(len(train_id)):
#     train_result.append(df.loc[df['result'] > 6])
# gkk = df.groupby(['gameid', 'team'])
# data_train = pd.DataFrame()
# for i in train_id:
#     data_train.append(gkk.get_group(i))
team_data = df.loc[df['player'] == 'Team']
X = team_data.iloc[:, 20:98]
cols = df.columns[20:98]
X[cols] = X[cols].apply(pd.to_numeric, errors='coerce')
# X = X[['fb', 'goldat15', 'oppgoldat15', 'gdat15', 'csat15', 'oppcsat15', 'csdat15']]
X = X[['fb', 'ft', 'fd', 'gdat10', 'csdat10', 'gdat15', 'csdat15']]

# X = X.fillna(0)
# # mid_stats = []
# # for cols in X.columns:
# #     if cols[-2:] == '10':
# #         mid_stats.append(cols)
# y = team_data.iloc[:, -1]

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# base = LDA()

# rfe = RFE(base, 5)
# rfe = rfe.fit(X, y)

# # features
# print(rfe.support_)
# print(rfe.ranking_)

# X = X[['fb', 'ft', 'fd', 'csdat10', 'csdat15']]
X = X.fillna(0)
y = team_data.iloc[:, -1]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

models = []

models.append(('LRG', LogisticRegression(solver='liblinear')))
# models.append(('KNB', KNeighborsClassifier()))
# models.append(('GNB', GaussianNB()))
# models.append(('XGB', xgb.XGBClassifier(random_state=0)))
# models.append(('RFC', RandomForestClassifier(random_state=0, n_estimators=100)))
# models.append(('DTC', DecisionTreeClassifier(random_state=0, criterion='entropy', max_depth=5)))

results = []
names = []

for name, m in models:
    kfold = model_selection.KFold(n_splits=5, random_state=0)
    cv_results = model_selection.cross_val_score(m, X, y, cv=kfold, scoring = 'roc_auc')
    results.append(cv_results)
    names.append(name)
    msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
    test = np.array([0, -1700, -35])
    test = test.reshape(1,-1)
    print(LogisticRegression.predict(self, X=test))
#create object of the lassifier
# neigh = KNeighborsClassifier(n_neighbors=3)
# #Train the algorithm
# neigh.fit(X_train, y_train)
# # predict the response
# pred = neigh.predict(X_test)
# # evaluate accuracy
# print("KNeighbors accuracy score : ",accuracy_score(y_test, pred))
#create an object of type LinearSVC
# svc_model = LinearSVC(random_state=0)
# #train the algorithm on training data and predict using the testing data
# pred = svc_model.fit(X_train, y_train).predict(X_test)
# #print the accuracy score of the model
# print("LinearSVC accuracy : ",accuracy_score(y_test, pred, normalize = True))
# #create an object of the type GaussianNB
gnb = GaussianNB()
# #train the algorithm on training data and predict using the testing data
gnb.fit(X_train, y_train)
# # test = np.array([0, -1700, -35])
# # test = test.reshape(1,-1)
pred = gnb.fit(X_train, y_train).predict(X_test)
# # predicted = gnb.predict(test)
# # print(f'predicted: {predicted}')
# #print(pred.tolist())
# #print the accuracy score of the model
print("Naive-Bayes accuracy : ",accuracy_score(y_test, pred, normalize = True))

# # output = pd.DataFrame()
# # output_s = pd.Series()
# for i in range(len(df)):
#     column_list = []
#     if df.iloc[i]['playerid'] in range(1, 6):
#         for col in df.keys():
#             column_list.append('{}_{}'.format(df.iloc[i]['playerid'], col))
#         test = pd.Series(df.iloc[i], index=column_list)
#         output_s.append(test)
#     output.append(output_s)
    # elif df.iloc[i]['playerid'] in range(6, 11):

# df['Over?'] = df.apply(line, axis=1)
# teams = {}
# team_number = 0
# for i in range(len(df)):
#     if df.iloc[i]['team'] in teams:
#         df['team number'] = teams[df.iloc[i]['team']]
#     else:
#         teams[df.iloc[i]['team']] = team_number
#         team_number += 1
#         df['team number'] = teams[df.iloc[i]['team']]
# with open('team_num.json', 'w') as outfile:
#     json.dump(teams, outfile, indent=4, sort_keys=True)
# player_data = df.loc[df['player'] != 'Team']


