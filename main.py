import os
from historic_parse import parse
from current import create_live2
import time
from joblib import load
import json
import pandas as pd
import numpy as np
from driver import init
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    url = 'https://sports.betway.com/en/sports/lve/esports'
    driver = init()
    driver.get(url)
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    #     (By.CSS_SELECTOR, "div[class='dropdownSelectedOptionText']"))).click()
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    #     (By.CSS_SELECTOR, "div[collectionitem='OddsAmerican']"))).click()
    file_list = []
    models = {420: '420v2_model.joblib',
              480: '480v2_model.joblib',
              540: '540v2_model.joblib',
              600: '600v2_model.joblib',
              660: '660v2_model.joblib',
              720: '720v2_model.joblib',
              780: '780v2_model.joblib',
              840: '840v2_model.joblib',
              900: '900v2_model.joblib',
              960: '960v2_model.joblib'}

    game = pd.DataFrame()
    count = 0
    while True:
        times, file_list = check_times(file_list)

        for file in times:
            with open(f'data/live/game/{file}.txt', 'r') as f:
                raw_data = json.load(f)
            try:
                df, check = parse(raw_data, 'live', file)
                game = game.append(df)
                print(f'File parsed: {file}')
            except:
                print(f'File not parsed b/c [{file}] broken')

            if file in models:
                model = load(models[file])
                cols = game.columns[2:25]
                game[cols] = game[cols].apply(pd.to_numeric, errors='coerce')
                predict = create_live2(game, file)
                prediction = np.array(predict)
                prediction = prediction.reshape(1, -1)
                predicted = model.predict(prediction)
                percentage = model.predict_proba(prediction)
                print(f'predicted: {predicted} | {percentage}')
                print(get_odds(file, driver))
            elif file == 0:
                print(get_odds(file, driver))

            else:
                print(f'Waiting{count * "."}', end='\r')
                if count > 5:
                    count = 0
            count += 1
        time.sleep(5)


def place_bets():
    pass


def get_odds(file, driver):
    odds = []
    teams = []
    containers_obj = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='container']")))

    teams_obj = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='oneLineScoreboard esports live']")))

    for y in teams_obj:
        team = y.text.split('\n')[-1].split(' -')
        teams.append(team)

    for x in containers_obj:
        try:
            odd = x.text.split('\n')
        except:
            odd = x
        odds.append(odd)

    pack = list(zip(teams, odds))

    with open(f'data/live/bets/{file}.txt', 'w') as f:
        json.dump(pack, f)
        print('Saved game')

    return pack


def check_times(file_list):
    files = os.listdir('data/live/game')
    if 'fix.txt' in files:
        files.remove('fix.txt')
    files = [int(x[:-4]) for x in files]
    check = list((set(file_list) | set(files)) - (set(file_list) & set(files)))
    check.sort()
    return check, files


if __name__ == '__main__':
    main()
