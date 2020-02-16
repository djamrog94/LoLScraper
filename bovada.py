from driver import *
import json


def get_odds(file):
    game = {}
    url = 'https://sports.betway.com/en/sports/lve/esports'
    options = Options()
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

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
        json.dump(game, f)
        print('Saved game')

    return pack
