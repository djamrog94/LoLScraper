import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import os
import xgboost as xgb
from sklearn.tree import DecisionTreeClassifier
from sklearn.calibration import CalibratedClassifierCV as CCV
from sklearn.ensemble import VotingClassifier
from joblib import dump
import numpy as np


def sort(r):
    line = r['path'].split('_')
    if '2020' in line:
        date = f'{line[-2]}/{line[-1]}/2020'
    else:
        date = f'{line[-2]}/{line[-1]}/2019'
    return date


def create_live2(df, time):
    df = df.fillna(0)
    player_df = df.loc[df['Time'] == time]
    player_df_1 = df.loc[df['Time'] == time - 60]
    player_df_3 = df.loc[df['Time'] == time - 180]

    # df for blue team, red team, and both sides players
    blue = player_df[:5]
    red = player_df[5:10]
    blue1 = player_df_1[:5]
    red1 = player_df_1[5:10]
    blue3 = player_df_3[:5]
    red3 = player_df_3[5:10]
    blue_team = player_df.iloc[10]
    red_team = player_df.iloc[11]

    # dmg metric
    blue_dmg = blue['CHAMPION DAMAGE'].sum() / (blue['CHAMPION DAMAGE'].sum() + red['MITIGATED DAMAGE'].sum())
    red_dmg = red['CHAMPION DAMAGE'].sum() / (red['CHAMPION DAMAGE'].sum() + blue['MITIGATED DAMAGE'].sum())
    dmg_metric = blue_dmg - red_dmg

    # gold % change metric
    blue_gold = blue['GOLD EARNED'].sum()
    blue_gold1 = blue1['GOLD EARNED'].sum()
    blue_gold3 = blue3['GOLD EARNED'].sum()

    red_gold = red['GOLD EARNED'].sum()
    red_gold1 = red1['GOLD EARNED'].sum()
    red_gold3 = red3['GOLD EARNED'].sum()

    try:
        b_cent_1 = (blue_gold - blue_gold1) / blue_gold1
        b_cent_3 = (blue_gold - blue_gold3) / blue_gold3

    except:
        b_cent_1 = np.nan
        b_cent_3 = np.nan
    try:
        r_cent_1 = (red_gold - red_gold1) / red_gold1
        r_cent_3 = (red_gold - red_gold3) / red_gold3
    except:
        r_cent_1 = np.nan
        r_cent_3 = np.nan
    try:
        cent_1 = b_cent_1 - r_cent_1
    except:
        cent_1 = np.nan
    try:
        cent_3 = b_cent_3 - r_cent_3
    except:
        cent_3 = np.nan

    # team metrics
    dragons = int(blue_team['Dragons'] - red_team['Dragons'])

    # player metrics
    vision = round(blue['VISION SCORE'].sum() - red['VISION SCORE'].sum(), 5)
    kills = int(blue['K'].sum() - red['K'].sum())
    predicted = [cent_1, cent_3, dmg_metric, dragons, kills, vision]
    return predicted


def create_live(df, time):
    fb = 0
    ft = 0
    fd = 0

    first = df.loc[df['playerid'] > 50]
    for i in range(len(first)):
        if first.iloc[i]['Kills'] != 0 and fb == 0:
            if i % 2 == 0:
                fb = 1
            else:
                fb = -1
        if first.iloc[i]['Towers'] != 0 and ft == 0:
            if i % 2 == 0:
                ft = 1
            else:
                ft = -1
        if first.iloc[i]['Dragons'] != 0 and fd == 0:
            if i % 2 == 0:
                fd = 1
            else:
                fd = -1

    player_df = df.loc[df['Time'] == time]
    blue = player_df[:5]
    red = player_df[5:10]
    vision = round(blue['VISION SCORE'].sum() - red['VISION SCORE'].sum(), 5)
    kills = int(blue['K'].sum() - red['K'].sum())
    assists = int(blue['A'].sum() - red['A'].sum())
    predict = [fb, ft, fd, vision, kills, assists]
    return predict


def create_dataset2():
    all_games = os.listdir('data/final')
    all_games = [x[:-5] for x in all_games]
    # df = pd.read_excel('420_df.xlsx')
    # done = list(df['path'])
    # games = (set(all_games) | set(done)) - (set(all_games) & set(done))
    intervals = {}

    # creates empty dict that will house each df
    for i in range(7, 28):
        intervals[i * 60] = [dict(), list()]

    for count, game in enumerate(all_games):
        df = pd.read_excel(f'data/final/{game}.xlsx')

        # for each minute within 7 - 17 minutes
        for interval in intervals:
            try:
                # df for current time, plus a min ago and 3 min ago
                player_df = df.loc[df['Time'] == interval]
                player_df_1 = df.loc[df['Time'] == interval - 60]
                player_df_3 = df.loc[df['Time'] == interval - 180]

                # df for blue team, red team, and both sides players
                blue = player_df[:5]
                red = player_df[5:10]
                blue1 = player_df_1[:5]
                red1 = player_df_1[5:10]
                blue3 = player_df_3[:5]
                red3 = player_df_3[5:10]
                blue_team = player_df.iloc[10]
                red_team = player_df.iloc[11]

                # dmg metric
                blue_dmg = blue['CHAMPION DAMAGE'].sum() / (blue['CHAMPION DAMAGE'].sum() + red['MITIGATED DAMAGE'].sum())
                red_dmg = red['CHAMPION DAMAGE'].sum() / (red['CHAMPION DAMAGE'].sum() + blue['MITIGATED DAMAGE'].sum())
                dmg_metric = blue_dmg - red_dmg

                # gold % change metric
                blue_gold = blue['GOLD EARNED'].sum()
                blue_gold1 = blue1['GOLD EARNED'].sum()
                blue_gold3 = blue3['GOLD EARNED'].sum()

                red_gold = red['GOLD EARNED'].sum()
                red_gold1 = red1['GOLD EARNED'].sum()
                red_gold3 = red3['GOLD EARNED'].sum()

                try:
                    b_cent_1 = (blue_gold - blue_gold1) / blue_gold1
                    b_cent_3 = (blue_gold - blue_gold3) / blue_gold3

                except:
                    b_cent_1 = np.nan
                    b_cent_3 = np.nan
                try:
                    r_cent_1 = (red_gold - red_gold1) / red_gold1
                    r_cent_3 = (red_gold - red_gold3) / red_gold3
                except:
                    r_cent_1 = np.nan
                    r_cent_3 = np.nan

                cent_1 = b_cent_1 - r_cent_1
                cent_3 = b_cent_3 - r_cent_3

                # team metrics
                baron = int(blue_team['Barons'].sum() - red_team['Barons'].sum())
                inhib = int(blue_team['Inhibitors'].sum() - red_team['Inhibitors'].sum())
                towers = int(blue_team['Towers'].sum() - red_team['Towers'].sum())
                dragons = int(blue_team['Dragons'].sum() - red_team['Dragons'].sum())

                # player metrics
                vision = round(blue['VISION SCORE'].sum() - red['VISION SCORE'].sum(), 5)
                cs = int(blue['MINION KILLS (CS)'].sum() - red['MINION KILLS (CS)'].sum())
                gold = int(blue['GOLD EARNED'].sum() - red['GOLD EARNED'].sum())
                kills = int(blue['K'].sum() - red['K'].sum())
                assists = int(blue['A'].sum() - red['A'].sum())
                intervals[interval][0].update({'path': game, 'vision': vision, 'cs': cs, 'kills': kills, 'assists': assists, 'gold': gold, 'damage': dmg_metric, 'cent_chg_1': cent_1, 'cent_chg_3': cent_3, 'baron': baron, 'inhib': inhib, 'towers': towers, 'dragons': dragons})
                intervals[interval][1].append(intervals[interval][0])
                intervals[interval][0] = {}
                print(f'Dataframe being created: ({count} / {len(all_games) - 1})')
            except:
                print(f'failed on {interval} | {game}')

    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    df4 = pd.DataFrame()
    df5 = pd.DataFrame()
    df6 = pd.DataFrame()
    df7 = pd.DataFrame()
    df8 = pd.DataFrame()
    df9 = pd.DataFrame()
    df10 = pd.DataFrame()
    df11 = pd.DataFrame()
    df12 = pd.DataFrame()
    df13 = pd.DataFrame()
    df14 = pd.DataFrame()
    df15 = pd.DataFrame()
    df16 = pd.DataFrame()
    df17 = pd.DataFrame()
    df18 = pd.DataFrame()
    df19 = pd.DataFrame()
    df20 = pd.DataFrame()

    dfs = [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14, df15, df16, df17, df18, df19, df20]
    results = pd.read_excel('results.xlsx')
    results = results.set_index('path')

    count = 420
    for df in dfs:
        df = pd.DataFrame(intervals[count][1])
        df['result'] = df.path.map(results.result)
        df.to_excel(f'{count}_df.xlsx', index=False)
        count += 60


def history_2():
    # loads in each time df created in create dataset function
    df1 = pd.read_excel('420_df.xlsx')
    df2 = pd.read_excel('480_df.xlsx')
    df3 = pd.read_excel('540_df.xlsx')
    df4 = pd.read_excel('600_df.xlsx')
    df5 = pd.read_excel('660_df.xlsx')
    df6 = pd.read_excel('720_df.xlsx')
    df7 = pd.read_excel('780_df.xlsx')
    df8 = pd.read_excel('840_df.xlsx')
    df9 = pd.read_excel('900_df.xlsx')
    df10 = pd.read_excel('960_df.xlsx')
    df11 = pd.read_excel('1020_df.xlsx')
    df12 = pd.read_excel('1080_df.xlsx')
    df13 = pd.read_excel('1140_df.xlsx')
    df14 = pd.read_excel('1200_df.xlsx')
    df15 = pd.read_excel('1260_df.xlsx')
    df16 = pd.read_excel('1320_df.xlsx')
    df17 = pd.read_excel('1380_df.xlsx')
    df18 = pd.read_excel('1440_df.xlsx')
    df19 = pd.read_excel('1500_df.xlsx')
    df20 = pd.read_excel('1560_df.xlsx')

    count = 420

    # trains model for each df, and saves the model
    for df in [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14, df15, df16, df17, df18, df19, df20]:
        train = pd.DataFrame()
        test = pd.DataFrame()
        df['Date'] = df.apply(sort, axis=1)
        for i in range(len(df)):
            if '2020' in df.iloc[i]['Date']:
                test = test.append(df.iloc[i])
            elif '2019' in df.iloc[i]['Date']:
                train = train.append(df.iloc[i])
        X_train = train[['cent_chg_1', 'cent_chg_3', 'damage', 'dragons', 'kills', 'vision']]
        y_train = train['result']
        X_test = test[['cent_chg_1', 'cent_chg_3', 'damage', 'dragons', 'kills', 'vision']]
        y_test = test['result']

        boost = xgb.XGBClassifier()
        dtc = DecisionTreeClassifier(max_depth=5, criterion='entropy')
        lrg = LogisticRegression(solver='liblinear')
        vote = VotingClassifier(estimators=[('boost', boost), ('dtc', dtc), ('lrg', lrg)], voting='soft')

        model = CCV(vote, method='isotonic', cv=3)
        model.fit(X_train, y_train)

        print(f'{count}: {model.score(X_test, y_test)}')
        dump(model, f'{count}v2_model.joblib')
        count += 60


def create_dataset():
    all_games = os.listdir('data/final')
    all_games = [x[:-5] for x in all_games]
    # df = pd.read_excel('test2.xlsx')
    # done = list(df['path'])
    # games = (set(all_games) | set(done)) - (set(all_games) & set(done))
    game_list_600 = []
    game_list_900 = []
    game_list_1200 = []
    game_list_1500 = []
    game_list_1800 = []

    for count, game in enumerate(all_games):
        game_dict_600 = {}
        game_dict_900 = {}
        game_dict_1200 = {}
        game_dict_1500 = {}
        game_dict_1800 = {}
        df = pd.read_excel(f'data/final/{game}.xlsx')
        fb = 0
        ft = 0
        fd = 0

        first = df.loc[df['playerid'] > 50]
        for i in range(len(first)):
            if first.iloc[i]['Kills'] != 0 and fb == 0:
                if i % 2 == 0:
                  fb = 1
                else:
                    fb = -1
            if first.iloc[i]['Towers'] != 0 and ft == 0:
                if i % 2 == 0:
                    ft = 1
                else:
                    ft = -1
            if first.iloc[i]['Dragons'] != 0 and fd == 0:
                if i % 2 == 0:
                    fd = 1
                else:
                    fd = -1

        intervals = {600: [game_dict_600, game_list_600],
                     900: [game_dict_900, game_list_900],
                     1200: [game_dict_1200, game_list_1200],
                     1500: [game_dict_1500, game_list_1500],
                     1800: [game_dict_1800, game_list_1800]}

        for interval in intervals:
            player_df = df.loc[df['Time'] == interval]
            blue = player_df[:5]
            red = player_df[5:10]
            vision = round(blue['VISION SCORE'].sum() - red['VISION SCORE'].sum(), 5)
            cs = int(blue['MINION KILLS (CS)'].sum() - red['MINION KILLS (CS)'].sum())
            kills = int(blue['K'].sum() - red['K'].sum())
            assists = int(blue['A'].sum() - red['A'].sum())
            gold = int(blue['GOLD EARNED'].sum() - red['GOLD EARNED'].sum())
            intervals[interval][0].update({'path': game, 'fb': fb, 'ft': ft, 'fd': fd, 'vision': vision, 'cs': cs, 'kills': kills, 'assists': assists, 'gold': gold})
            intervals[interval][1].append(intervals[interval][0])
            print(f'Dataframe being created: ({count} / {len(all_games) - 1 * 5})')

    df_600 = pd.DataFrame(game_list_600)
    df_900 = pd.DataFrame(game_list_900)
    df_1200 = pd.DataFrame(game_list_1200)
    df_1500 = pd.DataFrame(game_list_1500)
    df_1800 = pd.DataFrame(game_list_1800)

    results = pd.read_excel('results.xlsx')
    results = results.set_index('path')
    df_600['result'] = df_600.path.map(results.result)
    df_900['result'] = df_900.path.map(results.result)
    df_1200['result'] = df_1200.path.map(results.result)
    df_1500['result'] = df_1500.path.map(results.result)
    df_1800['result'] = df_1800.path.map(results.result)

    # main = pd.read_excel('test1.xlsx')
    # main = main.append(df)

    # main['Date'] = main.apply(sort, axis=1)
    # main['Date'] = pd.to_datetime(main['Date'])
    # main = main.sort_values(by=['Date'])
    df_600.to_excel('test_600.xlsx', index=False)
    df_900.to_excel('test_900.xlsx', index=False)
    df_1200.to_excel('test_1200.xlsx', index=False)
    df_1500.to_excel('test_1500.xlsx', index=False)
    df_1800.to_excel('test_1800.xlsx', index=False)
    print(df_600)


def history():
    df_600 = pd.read_excel('test_600.xlsx')
    df_900 = pd.read_excel('test_900.xlsx')
    df_1200 = pd.read_excel('test_1200.xlsx')
    df_1500 = pd.read_excel('test_1500.xlsx')
    df_1800 = pd.read_excel('test_1800.xlsx')
    count = 600

    for df in [df_600, df_900, df_1200, df_1500, df_1800]:
        train = pd.DataFrame()
        test = pd.DataFrame()
        df['Date'] = df.apply(sort, axis=1)
        for i in range(len(df)):
            if '2020' in df.iloc[i]['Date']:
                test = test.append(df.iloc[i])
            elif '2019' in df.iloc[i]['Date']:
                train = train.append(df.iloc[i])
        X_train = train[['fb', 'ft', 'fd', 'vision', 'kills', 'assists']]
        y_train = train['result']
        X_test = test[['fb', 'ft', 'fd', 'vision', 'kills', 'assists']]
        y_test = test['result']

        boost = xgb.XGBClassifier()
        dtc = DecisionTreeClassifier(max_depth=5, criterion='entropy')
        lrg = LogisticRegression(solver='liblinear')
        vote = VotingClassifier(estimators=[('boost', boost), ('dtc', dtc), ('lrg', lrg)], voting='soft')

        model = CCV(vote, method='isotonic', cv=3)
        model.fit(X_train, y_train)

        dump(model, f'{count}_model.joblib')
        count += 300

    # df = pd.read_excel('test2.xlsx')
    # df.fillna(0, inplace=True)
    # tr_score = []
    # ts_score = []
    # X = df.iloc[:, 1:9]
    # cols = df.columns[1:9]
    # X[cols] = X[cols].apply(pd.to_numeric, errors='coerce')
    # X = X.fillna(0)
    # y = df.iloc[:, -1]
    # for j in range(1000):
    #     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=j)
    #     clf = LogisticRegression(solver='liblinear').fit(X_train, y_train)
    #     tr_score.append(clf.score(X_train, y_train))
    #     ts_score.append(clf.score(X_test, y_test))
    #     print(f'Tested possibility: {j}')
    # J = ts_score.index(np.max(ts_score))
    # X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=J, test_size=0.2)
    # clf = LogisticRegression(solver='liblinear').fit(X_train, y_train)
    #
    # print(f'Training score: {clf.score(X_train, y_train)}')
    # print(f'Testing score: {clf.score(X_test, y_test)}')
    # dump(clf, 'test_model2.joblib')


# create_dataset()



if __name__ == '__main__':
    create_dataset2()
    history_2()
