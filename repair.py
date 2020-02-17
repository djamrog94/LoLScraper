from driver import *
import pandas as pd


def main():
    repair_folders = os.listdir('data/critical')
    repair_folders = [x[:-5] for x in repair_folders]
    for folder in repair_folders:
        repair(folder)


def repair_parse(driver, fix, yt_end, file_name):
    # a lot of repeated code from driver function
    game = True

    try:
        # error handle
        while True:
            players = WebDriverWait(driver, 45).until(EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='hero-selector__hero__name']")))
            heroes = driver.find_element_by_xpath("//div[@class='lol-stats-comparison__heros']").text
            test = heroes.split('\n')[2].split('-')
            if len(players) == 10 and len(test) == 2:
                break

        elem_video = driver.find_element_by_css_selector("div[class^='Footerstyles__Timestamp']"). \
            get_attribute('innerHTML')
        game_start, _ = elem_video.split(' / ')
        game_start = convert_time(game_start)
        print(f'Game: {file_name} is beginning. Parsing starting now... ')

        while len(fix) > 0:
            searching = True
            stats5 = []
            current = fix.pop(0)
            driver.execute_script(f'document.getElementsByTagName("video")[0].currentTime={game_start + current - 5}')
            # start the parse"div[class^='Footerstyles__Timestamp']"
            while searching:
                # calculate current game time
                elem_video = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[class^='Footerstyles__Timestamp']"))).get_attribute('innerHTML')

                current_time, _ = elem_video.split(' / ')
                current_time = convert_time(current_time)
                game_time = int(current_time - game_start)

                if game_time == current:
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
                    with open(f'data/{file_name}/game_info.txt', 'w') as f:
                        f.write(f'{game_start},{yt_end}')

                    completed = int((current_time / yt_end) * BAR_LENGTH)
                    bar = '[' + ('#' * completed) + ('.' * (BAR_LENGTH - completed)) + ']'
                    time_left = int((yt_end - current_time) * 2.2)
                    time_left = str(datetime.timedelta(seconds=time_left))
                    print(f'Progress: {game_time}; {current_time} / {yt_end} | {bar} || Approx. time left: {time_left}.',
                          end='\r')
                    driver.find_element_by_tag_name('body').send_keys(Keys.SPACE)
                    searching = False
    except ValueError as e:
        print(f'failed! {e}')
        driver.quit()

    finally:
        # if game completed
        if game is False:
            with open('bts.txt', 'r') as f:
                last_game = int(f.readline())
            with open('bts.txt', 'w') as f:
                f.write(str(last_game + 1))
            driver.quit()


def repair(path):
    # opens up fix.txt file for game, repairs each 5 second block of data that is broken
    with open(f'data/{path}/fix.txt', 'r') as f:
        numbers = f.readlines()
        numbers = [int(x[:-5]) for x in numbers]

    schedule = pd.read_excel('schedule.xlsx')
    index = schedule.loc[schedule[1] == path].index[0]
    index = schedule.iloc[index]['index']
    driver = init()
    navigate(driver)
    games = find_game(driver)
    game = games[index]
    file_name, game_link = start_game(driver, game)
    game_link.click()
    yt_end = find_start(driver)

    repair_parse(driver, numbers, yt_end, file_name)


if __name__ == '__main__':
    main()
