from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

PIXELS = 1875

def match(text):
    pattern = r'(?<=left:).*?px'
    m = re.search(pattern, text)
    output = m.group(0)[:-2].lstrip()
    return float(output)

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


def main():
    options = Options()
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.get('https://watch.lolesports.com/pro-view/vods')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='riotbar-anonymous-link riotbar-account-action']"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys('jamfrog')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys('Vohabdmj2')
    driver.find_element_by_css_selector("div.grid.grid-direction__column div.grid.grid-direction__column.auth-rso-login-page.grid-page.grid-page-web.grid-page-web--theme-riot div.grid.grid-direction__row.grid-page-web__content:nth-child(2) div.grid.grid-direction__column.grid-page-web__wrapper div.grid.grid-direction__column.grid-size-17.grid-panel-web.grid-panel.grid-panel-web-has-links > button.mobile-button.mobile-button--theme-riot.mobile-button__submit:nth-child(3)").click()
    frame = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
    driver.switch_to.frame(frame)
    elem_start = driver.find_element_by_xpath("//div[@class='game-action'][contains(text(),'GAME')]").get_attribute('outerHTML')
    elem_end = driver.find_element_by_xpath("//div[@class='game-action'][contains(text(),'POST GAME')]").get_attribute('outerHTML')
    elem_video = driver.find_element_by_xpath("//div[@class='Footerstyles__Timestamp-sc-1wqvr1n-3 YyptY']").get_attribute('innerHTML')
    _, time = elem_video.split(' / ')
    video_length = convert_time(time)
    game_start = match(elem_start)
    game_end = match(elem_end)
    yt_start = (game_start / PIXELS) * video_length
    yt_end = (game_end / PIXELS) * video_length
    print(f'start: {yt_start} | end: {yt_end}')

main()










    # driver.execute_script(f'document.getElementsByTagName("video")[0].currentTime={x}')
    # driver.switch_to.default_content()
    # while True:
    #     try:
    #         WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "blue-team")))
    #         x -= 30
    #         driver.switch_to.frame('video-player-youtube')
    #         driver.execute_script(f'document.getElementsByTagName("video")[0].currentTime={x}')
    #         driver.switch_to.default_content()
    #         time.sleep(2)
    #     except:
    #         WebDriverWait(driver, 120).until(EC.presence_of_element_located(
    #             (By.XPATH, "//div[@class='blue-team'][contains(text(),'2.5 K')]")))
    #         driver.switch_to.frame('video-player-youtube')
    #         elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
    #             (By.XPATH, "//div[@class='ytp-time-display notranslate']")))
    #         youtube_start = elem.find_element_by_class_name("ytp-time-current").get_attribute('innerHTML')
    #         youtube_end = elem.find_element_by_class_name("ytp-time-duration").get_attribute('innerHTML')
    #         break
    # driver.quit()
    # with open("test.txt", "a") as f:
    #     f.write(f'{youtube_start}\n')
