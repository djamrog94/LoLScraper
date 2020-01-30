import pandas as pd
import datetime as dt

def fantasy_score(r):
    score = 0
    if r['player'] != 'Team':
        if r['k'] >= 10 or r['a'] >= 10:
            score = (r['k'] * 3) + (r['a'] * 2) + (r['d'] * -1) + (r['minionkills'] * 0.02) + 2
        else:
            score = (r['k'] * 3) + (r['a'] * 2) + (r['d'] * -1) + (r['minionkills'] * 0.02)
    else:
        try:
            if r['gamelength'] > 30:
                score = (r['teamtowerkills'] * 1) + (r['teamdragkills'] * 2) + (r['teambaronkills'] * 3) + (r['fb'] * 2) +\
                    (r['result'] * 2)
            else:
                score = (r['teamtowerkills'] * 1) + (r['teamdragkills'] * 2) + (r['teambaronkills'] * 3) + (r['fb'] * 2) + \
                        (r['result'] * 2) + 2
        except:
            print('Failed')
    percent = r['Unnamed: 0'] / len(df)
    print('Updated fantasy score for {}. {}% completed'.format(r['player'], percent))
    return score



df = pd.read_excel('master_file.xlsx')
df = df.reset_index()
df = df[df.url.notnull()]
df['points'] = df.apply(fantasy_score, axis=1)
df.to_excel('master_file.xlsx')

def prepare():
    df['date'] = pd.TimedeltaIndex(df['date'], unit='d') + dt.datetime(1899, 12, 30)


