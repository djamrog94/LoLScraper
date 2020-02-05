from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import re
import json
import os
import datetime

BAR_LENGTH = 50
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 1080
PIXELS = WINDOW_WIDTH * (1875 / 1920)
SCROLL_PAUSE_TIME = 0.5


def main(variance):
    # find games
    with open('bt.txt', 'r') as f:
        last_game = int(f.readline()) + variance
    # parse all remaining games
    while True:
        driver = init()
        navigate(driver)
        games = find_game(driver)
        if last_game > len(games):
            break
        game = games[last_game]
        file_name, game_link = start_game(driver, game)
        game_link.click()
        yt_end = find_start(driver)
        parse(driver, yt_end, file_name)
        print(f'\nFinished parsing: {file_name}.')
        last_game += 3


def init():
    options = Options()
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
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
            value = WebDriverWait(driver, 7).until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, 'matches-date-wrapper')))
            return value
        except:
            driver.refresh()
            frame = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
            driver.switch_to.frame(frame)


def navigate(driver):
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
    frame = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
    driver.switch_to.frame(frame)
    time.sleep(4)
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def find_game(driver):
    # find last game parsed
    with open('bt.txt', 'r') as f:
        last_game = int(f.readline())
    # find all games
    schedule = error_handle(driver)
    games = []
    for x, week in enumerate(schedule):
        week_games = week.find_elements_by_class_name('riot-match-item')
        for game in week_games:
            games.insert(0, [x, game])
    return games


def start_game(driver, game):
    while True:
        try:
            schedule = error_handle(driver)
            matchup = game[1].text.split('\nVS\n')
            season = schedule[game[0]].text.split('\n')[0].replace(' ', '_')
            file_name = "_".join(matchup) + '_' + season
            break
        except TimeoutError as e:
            print(f'{e}. Trying again.')
            navigate(driver)
    return file_name, game[1]


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
    # yt_end = (game_end / PIXELS) * video_length
    driver.execute_script(f'document.getElementsByTagName("video")[0].currentTime={yt_start}')
    return video_length


def dump(data, game_time, file):
    isdir = os.path.isdir(f'data/{file}')
    if isdir:
        pass
    else:
        os.makedirs(f'data/{file}')
    path = f'data/{file}/{game_time}.txt'
    with open(path, 'w') as f:
        json.dump(data, f)


def parse(driver, yt_end, file_name):
    # check if game is mid game
    mid_start = 0
    try:
        files = os.listdir(f'data/{file_name}')
        if len(files) != 0:
            files = [int(x[:-4]) for x in files]
            mid_start = max(files)
    except:
        pass

    game = True
    try:
        # error handle
        while True:
            players = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='hero-selector__hero__name']")))
            heroes = driver.find_element_by_xpath("//div[@class='lol-stats-comparison__heros']").text
            test = heroes.split('\n')[2].split('-')
            if len(players) == 10 and len(test) == 2:
                break

        elem_video = driver.find_element_by_css_selector("div[class^='Footerstyles__Timestamp']").\
            get_attribute('innerHTML')
        game_start, _ = elem_video.split(' / ')
        game_start = convert_time(game_start)
        if mid_start != 0:
            driver.execute_script(f'document.getElementsByTagName("video")[0].currentTime={game_start + mid_start - 4}')
        print(f'Game: {file_name} is beginning. Parsing starting now... ')

        # start the parse
        while game is True:
            stats5 = []

            # calculate current game time
            elem_video = driver.find_element_by_css_selector("div[class^='Footerstyles__Timestamp']").get_attribute(
                'innerHTML')
            current_time, _ = elem_video.split(' / ')
            current_time = convert_time(current_time)
            game_time = int(current_time - game_start)

            # check if game is over
            if current_time >= (yt_end - 5):
                game = False

            if game_time % 5 == 0:
                driver.find_element_by_tag_name('body').send_keys(Keys.SPACE)
                stats5.append(game_time)
            # 5 second data
                for n in range(0, 10, 2):
                    players[n].click()
                    time.sleep(1)
                    heroes = driver.find_element_by_xpath("//div[@class='lol-stats-comparison__heros']").text
                    primary_stats = driver.find_element_by_xpath("//div[@class='advanced-stats']").text
                    stats5.append(heroes)
                    stats5.append(primary_stats)

                team_elem = driver.find_element_by_xpath("//div[@class='lol-team-stats']").text
                dragons = driver.find_elements_by_xpath("//div[@class='dragons__wrapper']")
                blue_dragons_h, red_dragons_h = dragons[0].get_attribute('innerHTML'), \
                                                dragons[1].get_attribute('innerHTML')
                blue_dragons = blue_dragons_h.count('dragon')
                red_dragons = red_dragons_h.count('dragon')
                stats5.append(team_elem)
                stats5.append(blue_dragons)
                stats5.append(red_dragons)

                dump(stats5, game_time, file_name)

                completed = int((current_time / yt_end) * BAR_LENGTH)
                bar = '[' + ('#' * completed) + ('.' * (BAR_LENGTH - completed)) + ']'
                time_left = int((yt_end - current_time) * 2.2)
                time_left = str(datetime.timedelta(seconds=time_left))
                print(f'Progress: {game_time}; {current_time} / {yt_end} | {bar} || Approx. time left: {time_left}.', end='\r')
                driver.find_element_by_tag_name('body').send_keys(Keys.SPACE)
                time.sleep(1)
    except ValueError as e:
        print(f'failed! {e}')

    finally:
        # if game completed
        if game is False:
            with open('bt.txt', 'r') as f:
                last_game = int(f.readline())
            with open('bt.txt', 'w') as f:
                f.write(str(last_game + 1))
            driver.quit()


if __name__ == '__main__':
    main()
