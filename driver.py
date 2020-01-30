from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from parser import parse_text, parse_team
import pandas as pd
import re

PIXELS = 1875


def main():
    """
    url = str. link to VOD page
    saved_time = str. time in seconds of game time when prior run broke
    yt_start = str. time in normal form of when game starts in video
    continue_time = int. time in seconds where video should play. either start of video or where broke in prior run
    :return:
    """
    file = open("bt.txt", "r")
    load_time = file.readlines()
    if len(load_time) == 3:
        url = load_time[0]
        saved_time = int(load_time[1])
        yt_start = load_time[2]
        df = pd.read_hdf('data/CLGDIGwk120.h5')
    else:
        df = pd.DataFrame
        # df = pd.DataFrame(
        #     columns=['Game Time', 'Name', 'Champ', 'Role', 'Kills', 'Deaths', 'Assists', 'Gold Earned', 'CS',
        #              'Kill Participation', 'Champ Damage Share', 'Wards Placed', 'Wards Destroyed', 'Attack Damage',
        #              'Ability Power', 'Critical Chance', 'Attack Speed', 'Life Steal', 'Armor', 'Magic Resist',
        #              'Tenacity',
        #              'Dragons', 'Inhibitors', 'Barons', 'Towers'])
        url = 'https://watch.lolesports.com/vod/103462440145619685/1/UUI1CTsoses'
        saved_time = 0
        yt_start = ''
    driver = init()
    driver.get(url)
    parse(driver, df, saved_time, yt_start, url)


def init():
    options = Options()
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver


def convert_time(time):
    """
    function convert_time converts time to seconds
    :param time: input as string
    :return: int
    """
    hours = 0
    try:
        hours, minutes, seconds = time.split(':')
    except:
        minutes, seconds = time.split(':')
    output = (int(hours) * 60 * 60) + int(minutes) * 60 + int(seconds)
    return output


def match(text):
    pattern = r'(?<=left:).*?px'
    m = re.search(pattern, text)
    output = m.group(0)[:-2].lstrip()
    return float(output)

# TODO  save index of current game!
def find_game(driver):
    with open('bt.txt', 'r') as f:
        last_game = int(f.readline())
    schedule = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "matches-date-wrapper")))
    games = []
    for x, week in enumerate(schedule):
        week_games = week.find_elements_by_class_name('riot-match-item')
        for game in week_games:
            games.append([x, game])
    current = games[-last_game - 1]
    matchup = current[1].text.split('\nVS\n')
    season = schedule[current[0]].text.split('\n')[0].replace(' ', '_')
    file_name = "_".join(matchup) + season
    return current[1], file_name


def find_start(driver):
    driver.get('https://watch.lolesports.com')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//a[@class='riotbar-anonymous-link riotbar-account-action']"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys('jamfrog')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys('Vohabdmj2')
    driver.find_element_by_css_selector("div.grid.grid-direction__column div.grid.grid-direction__column.auth-rso-login-page.grid-page.grid-page-web.grid-page-web--theme-riot div.grid.grid-direction__row.grid-page-web__content:nth-child(2) div.grid.grid-direction__column.grid-page-web__wrapper div.grid.grid-direction__column.grid-size-17.grid-panel-web.grid-panel.grid-panel-web-has-links > button.mobile-button.mobile-button--theme-riot.mobile-button__submit:nth-child(3)").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "title-text"))).click()
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "proViewVods"))).click()
    frame = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
    driver.switch_to.frame(frame)
    current, file_name = find_game(driver)
    current.click()
    elem_start = driver.find_element_by_xpath("//div[@class='game-action'][contains(text(),'GAME')]")\
        .get_attribute('outerHTML')
    elem_end = driver.find_element_by_xpath("//div[@class='game-action'][contains(text(),'POST GAME')]")\
        .get_attribute('outerHTML')
    elem_video = driver.find_element_by_css_selector("div[class^='Footerstyles__Timestamp']").get_attribute('innerHTML')
    _, vid_time = elem_video.split(' / ')
    video_length = convert_time(vid_time)
    game_start = match(elem_start)
    game_end = match(elem_end)
    yt_start = (game_start / PIXELS) * video_length
    yt_end = (game_end / PIXELS) * video_length
    return yt_start, yt_end, file_name


def parse(driver, df, saved_time, yt_start, url):
    """
    game_start: float. time.time of when game starts
    game_time: int. how many seconds game has been going on for
    youtube_start = str. normal format when games starts according to yt
    youtube_end = str. normal format when entire video ends according to yt

    :param driver:
    :param df:
    :param continue_time: int. time in seconds where video should play. either start of video or where broke in prior run
    :param url:
    :return:
    """
    game_start = 0
    game_time = saved_time
    youtube_start = yt_start
    youtube_end = ''
    blue_team = ''
    red_team = ''
    game = True
    total_stats = []
    try:
        # if new game find when game starts
        if youtube_start == '':
            print(f'This is a new game: finding starting location now.')
            youtube_start, youtube_end, file_name = find_start(driver)
        else:
            print(f'Picking up from prior game.')
        youtube_start = youtube_start
        youtube_end = youtube_end

        # moving video to start of game
        driver.execute_script(f'document.getElementsByTagName("video")[0].currentTime={youtube_start + game_time}')
        game_start = time.time()
        print(f'Game is beginning. Parsing starting now... ')
        # driver.switch_to.default_content()
        # start the parse
        while game is True:
            # while game is going on every second look at each matchup and download detailed stats
            # for role in ['jungle', 'mid', 'bottom', 'support', 'top']:
            stats = []
            game_time = int(time.time() - game_start)
            stats.append(game_time)
            if game_time > youtube_end:
                game = False
            for n in [0, 1, 2, 3, 0]:
                WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@class='hero-selector']")))[n].click()
                time.sleep(.5)
                #T ODO Have raw data for players, teams, dragons. just need to parse
                primary_stats = driver.find_elements_by_xpath("//div[@class='advanced-stats']")
                for i in primary_stats:
                    stats.append(i.text)
                team_elem = driver.find_elements_by_xpath("//div[@class='lol-team-stats']")
                for i in team_elem:
                    stats.append(i.text)
                dragons = driver.find_elements_by_xpath("//div[@class='dragons__wrapper']")
                blue_dragons_h, red_dragons_h = dragons[0].get_attribute('innerHTML'),\
                                                dragons[1].get_attribute('innerHTML')
                blue_dragons = blue_dragons_h.count('dragon')
                red_dragons = red_dragons_h.count('dragon')
                stats.append(blue_dragons)
                stats.append(red_dragons)
                # primary_stats = driver.find_elements_by_xpath("//div[@class='player primary']")
                # _, blue_data, blue_team = parse_text(primary_stats, game_time)
                # second_stats = driver.find_elements_by_xpath("//div[@class='player secondary']")
                # _, red_data, red_team = parse_text(second_stats, game_time)
                # df.loc[len(df)] = blue_data
                total_stats.append(stats)
                print(f'Progress: ({game_time} / {youtube_end} | {(game_time / youtube_end):3f})')
            # get team data
            # team_stats = driver.find_elements_by_xpath("//div[@class='StatsTeamsSummary']")
            # dragons = team_stats[0].get_attribute('innerHTML')
            # blue_team_data, red_team_data = parse_team(team_stats, dragons, game_time, blue_team, red_team)
            # df.loc[len(df)] = blue_team_data
            # df.loc[len(df)] = red_team_data

    except:
        print('failed!')
        # quit driver and write file to save progress
        # file = open("bt.txt", "w+")
        # file.write(url)
        # file.write(str(game_time))
        # file.write(str(youtube_start))
    finally:
        # quit driver and write file
        driver.quit()
        if game is False:
            file = open("bt.txt", "w+")
            file.write('')
        df = pd.DataFrame(data=total_stats)
        df.to_hdf(file_name, key='df', mode='w')


if __name__ == '__main__':
    main()

