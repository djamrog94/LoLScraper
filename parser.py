import os
import shutil
import json
import pandas as pd
import numpy as np

review = 0
final = 0


# function to convert the list containing 5 second data to df which will be appended to main game df
def parse(input_data, path, file):
    blue_team = {}
    red_team = {}
    payload = input_data
    time = payload[0]
    b = []
    r = []
    check = False
    for x in range(1, 10, 2):
        count = 0
        data = payload[x].split('\n')
        b_name = data[1]
        r_name = data[8]
        b.append(b_name)
        r.append(r_name)
        for team in ['blue', 'red']:
            for obj in ['name', 'role', 'health', 'mana', 'AD', 'AP']:
                if count in [0, 7]:
                    if team == 'blue':
                        count += 1
                        blue_team[data[count]] = {}
                    else:
                        count += 1
                        red_team[data[count]] = {}
                elif count in [2, 9]:
                    if team == 'blue':
                        blue_team[b_name]['role'] = data[count].split(' - ')[0]
                        blue_team[b_name]['champ'] = data[count].split(' - ')[1]
                    else:
                        red_team[r_name]['role'] = data[count].split(' - ')[0]
                        red_team[r_name]['champ'] = data[count].split(' - ')[1]

                else:
                    if team == 'blue':
                        blue_team[b_name][f'{obj}'] = data[count]
                    else:
                        red_team[r_name][f'{obj}'] = data[count]
                count += 1

        attr = payload[x + 1].split('\n')
        for n in range(len(attr)):
            if n in [0, 24]:
                if n == 0:
                    kills, deaths, assists = attr[n].split((' / '))
                    k, d, a = attr[n + 1].split((' / '))
                    kda = dict(zip([k, d, a], [kills, deaths, assists]))
                    for key in kda:
                        blue_team[b_name][key] = kda[key]
                else:
                    kills, deaths, assists = attr[n].split((' / '))
                    k, d, a = attr[n + 1].split((' / '))
                    kda = dict(zip([k, d, a], [kills, deaths, assists]))
                    for key in kda:
                        red_team[r_name][key] = kda[key]

            else:
                if n % 2 == 0:
                    if n < 24:
                        blue_team[b_name][attr[n + 1]] = attr[n]
                    else:
                        red_team[r_name][attr[n + 1]] = attr[n]

    team_data = payload[11].split('\n')
    b_team_name = team_data[14].split(' ')[0]
    r_team_name = team_data[20].split(' ')[0]
    blue_team[b_team_name] = {}
    red_team[r_team_name] = {}
    for index, team in enumerate(['blue', 'red']):
        for index1, tag in enumerate(['Inhibitors', 'Barons', 'Towers', 'Kills']):
            if tag == 'Kills':
                value = team_data[index1 + 5 + (index * 5)]
            else:
                value = team_data[index1 + 4 + (index * 5)]
            if team == 'blue':
                blue_team[b_team_name][tag] = value
            else:
                red_team[r_team_name][tag] = value

    blue_team[b_team_name]['Gold'] = team_data[1]
    red_team[r_team_name]['Gold'] = team_data[3]
    blue_team[b_team_name]['Dragons'] = payload[12]
    red_team[r_team_name]['Dragons'] = payload[13]

    blue_df = pd.DataFrame.from_dict(blue_team, orient='columns').T
    red_df = pd.DataFrame.from_dict(red_team, orient='columns').T
    output = blue_df.append(red_df)
    output['Time'] = time
    try:
        output['playerid'] = [1, 2, 3, 4, 5, 100, 6, 7, 8, 9, 10, 200]
    except:
        check = True
        with open(f'data/{path}/fix.txt', 'a') as outfile:
            outfile.write(f'{file}\n')
        print(f'Fails saved for {path}/{file}')

    return output, check

# function that takes all the 5 second df made from parse function and creates full game df
def create_game(path):
    global review
    global final
    path = path
    files = os.listdir(f'data/{path}')
    game = pd.DataFrame()
    a = False
    if len(files) != 0:
        for file in files:
            try:
                with open(f'data/{path}/{file}', 'r') as infile:
                    in_data = json.load(infile)
                    data, check = parse(in_data, path, file)
                    if check is True:
                        a = True
                    game = game.append(data)
            except:
                pass

        # sorts game by time and player id
        game = game.sort_values(by=['Time', 'playerid'])
        game = game.reset_index()
        game.rename(columns={'index': 'Name'}, inplace=True)

        # quick and dirty way to check if game over.
        # assume that if game gold hasn't changed in over 10 seconds, game is over
        last = game.iloc[-1]['Gold']
        index = game.loc[game['Gold'] == last].index
        game = game[:index[0] + 1]

        # if one of the 5 second df can't be formed; run repair function to fix broken times
        if a is True:
            game.to_excel(f'data/critical/{path}.xlsx', index=False)
            print(f'Saved to critical b/c missing data: {path}.')
            review += 1

        # seems likely that game did not finish, must double check before moving to final folder
        elif len(index) < 2:
            game.to_excel(f'data/review/{path}.xlsx', index=False)
            print(f'Saved to review might be too short: {path}.')
            review += 1

        # game sucessfully parsed; saved to final folder
        else:
            game.to_excel(f'data/final/{path}.xlsx', index=False)
            print(f'Saved to final: {path}.')
            shutil.move(f'data/{path}', 'data/backup')
            final += 1


def main():
    # try creating games; printing success / failures
    # only parses games that have not been parsed before
    fail = 0
    all_games = os.listdir(f'data')
    check = os.listdir(f'data/final')
    check = [x[:-5] for x in check]
    unique = (set(all_games) | set(check)) - (set(all_games) & set(check))
    for game in unique:
        try:
            create_game(game)

        except:
            print(f'Failed on: {game}')
            fail += 1

    print('********REPORT***********')
    print(f'{len(all_games)} games in total.\n'
          f' {final} games completed.\n'
          f' {review} games need to be reviewed.\n'
          f'{fail} games failed.\n'
          f'******END REPORT********')


if __name__ == '__main__':
    main()

