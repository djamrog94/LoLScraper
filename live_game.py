from driver import init
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json


def live_parse():
    driver = init()
    driver.get('https://watch.lolesports.com/')
    WebDriverWait(driver, 50).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//a[@class='riotbar-anonymous-link riotbar-account-action']"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys('jamfrog')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys('Vohabdmj2')
    driver.find_elements_by_tag_name("button")[1].click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "title-text"))).click()
    time.sleep(2)
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "proViewWatch"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "proViewVods"))).click()
    time.sleep(10)
    frame = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
    driver.switch_to.frame(frame)
    game = True
    try:
        # error handle

        count = 0
        while True:
            try:
                time.sleep(1)
                print(f'Waiting for game to start...{count}', end='\r')
                count += 1
                test = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='lol-stats-comparison__heros__hero__info__meta']")))
                if test.text.split('\n')[0] != '0':
                    break
            except:
                pass

        game_start = time.time()
        print('\nGame starting!')
        count = 0
        variance = 0
        # start the parse
        while game is True:
            stats5 = []
            # game_time = int(time.time() - game_start - (count * 5))
            game_time = int(time.time() - game_start + variance)
            players = WebDriverWait(driver, 50).until(EC.presence_of_all_elements_located(
                 (By.XPATH, "//div[@class='hero-selector__hero__name']")))
            if game_time % 60 == 0 and game_time != 0:
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

                with open(f'data/live/game/{game_time}.txt', 'w') as f:
                    json.dump(stats5, f)
                print(f'Saved file... {game_time}')

                driver.find_element_by_tag_name('body').send_keys(Keys.SPACE)
                for i in range(3):
                    driver.find_element_by_tag_name('body').send_keys(Keys.ARROW_RIGHT)
                    time.sleep(.1)
                count += 1
            else:
                print(f'Waiting... {game_time}', end='\r')
                time.sleep(1)
    except ValueError as e:
        print(f'failed! {e}')
        driver.quit()

    finally:
        driver.quit()


live_parse()
