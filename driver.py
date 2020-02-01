from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

BAR_LENGTH = 50
WINDOW_WIDTH = 1920
PIXELS = WINDOW_WIDTH * (1875 / 1920)


def main():
    driver = init()

    # find games
    games = find_game(driver)

    # parse all remaining games
    while len(games) > 0:
        game = games.pop(-1)
        file_name = start_game(driver, game)
        yt_end = find_start(driver)
        parse(driver, yt_end, file_name)


def init():
    options = Options()
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument(f"--window-size={WINDOW_WIDTH},1080")
    driver = webdriver.Chrome(options=options)
    return driver


def convert_time(g_time):
    hours = 0
    try:
        hours, minutes, seconds = g_time.split(':')
    except:
        minutes, seconds = g_time.split(':')
    output = (int(hours) * 60 * 60) + int(minutes) * 60 + int(seconds)
    return output


def match(text):
    pattern = r'(?<=left:).*?px'
    m = re.search(pattern, text)
    output = m.group(0)[:-2].lstrip()
    return float(output)


def error_handle(driver):
    while True:
        try:
            value = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, 'matches-date-wrapper')))
            return value
        except:
            driver.refresh()
            frame = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
            driver.switch_to.frame(frame)


def find_game(driver):
    # login and navigate to VOD page
    driver.get('https://watch.lolesports.com')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//a[@class='riotbar-anonymous-link riotbar-account-action']"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys('jamfrog')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys('Vohabdmj2')
    driver.find_elements_by_tag_name("button")[1].click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "title-text"))).click()
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "proViewVods"))).click()
    frame = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
    driver.switch_to.frame(frame)

    # find last game parsed
    with open('bt.txt', 'r') as f:
        last_game = int(f.readline())
    if last_game == 0:
        last_game = 1
    # find all games
    schedule = error_handle(driver)
    games = []
    for x, week in enumerate(schedule):
        week_games = week.find_elements_by_class_name('riot-match-item')
        for game in week_games:
            games.append([x, game])
    games = games[:-last_game]

    # return list
    return games


def start_game(driver, game):
    schedule = error_handle(driver)
    matchup = game[1].text.split('\nVS\n')
    season = schedule[game[0]].text.split('\n')[0].replace(' ', '_')
    file_name = "_".join(matchup) + '_' + season
    game[1].click()
    return file_name


def find_start(driver):
    elem_start = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, "//div[@class='game-action'][contains(text(),'GAME')]"))).get_attribute('outerHTML')
    elem_end = driver.find_element_by_xpath("//div[@class='game-action'][contains(text(),'POST GAME')]") \
        .get_attribute('outerHTML')
    elem_video = driver.find_element_by_css_selector("div[class^='Footerstyles__Timestamp']").get_attribute('innerHTML')
    _, vid_time = elem_video.split(' / ')
    video_length = convert_time(vid_time)
    game_start = match(elem_start)
    game_end = match(elem_end)
    yt_start = (game_start / PIXELS) * video_length
    yt_end = (game_end / PIXELS) * video_length
    driver.execute_script(f'document.getElementsByTagName("video")[0].currentTime={yt_start}')
    return int(yt_end)


def parse(driver, yt_end, file_name):
    game = True
    total_stats5 = []
    youtube_end = yt_end
    try:
        game_start = time.time()
        print(f'Game is beginning. Parsing starting now... ')
        time.sleep(5)

        # start the parse
        while game is True:
            stats5 = []
            # calculate current game time
            game_time = int(time.time() - game_start)
            stats5.append(game_time)

            # check if game is over
            if game_time > youtube_end:
                game = False

            # seconds data
            team_elem = driver.find_element_by_xpath("//div[@class='lol-team-stats']").text
            dragons = driver.find_elements_by_xpath("//div[@class='dragons__wrapper']")
            blue_dragons_h, red_dragons_h = dragons[0].get_attribute('innerHTML'), \
                                            dragons[1].get_attribute('innerHTML')
            blue_dragons = blue_dragons_h.count('dragon')
            red_dragons = red_dragons_h.count('dragon')
            stats5.append(team_elem)
            stats5.append(blue_dragons)
            stats5.append(red_dragons)
            # error handle
            while True:
                players = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@class='hero-selector__hero__name']")))
                if len(players) == 10:
                    break

            # 5 second data
            for n in range(0, 10, 2):
                players[n].click()
                time.sleep(1)
                heroes = driver.find_element_by_xpath("//div[@class='lol-stats-comparison__heros']").text
                primary_stats = driver.find_element_by_xpath("//div[@class='advanced-stats']").text
                stats5.append(heroes)
                stats5.append(primary_stats)
                print(f'{heroes}')
                completed = int((game_time / youtube_end) * BAR_LENGTH)
                bar = '[' + ('#' * completed) + ('.' * (BAR_LENGTH - completed)) + ']'
                print(f'Progress: ({game_time} / {youtube_end} | {((game_time / youtube_end) * 100):.2f}%) || {bar}')
            total_stats5.append(stats5)

    except ValueError as e:
        print(f'failed! {e}')

    finally:
        driver.quit()

        # if game completed
        if game is False:
            with open('bt.txt', 'r') as f:
                last_game = int(f.readline())
            with open('bt.txt', 'w') as f:
                f.write(str(last_game + 1))
            df5 = pd.DataFrame(data=total_stats5)
            df5.to_hdf(f'data/{file_name}.h5', key='df', mode='w')


if __name__ == '__main__':
    main()
