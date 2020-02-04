from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

options = Options()
options.add_argument("--autoplay-policy=no-user-gesture-required")
options.add_argument(f"--window-size=1400,1080")
driver = webdriver.Chrome(options=options)

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
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='RiotVODs__SelectedLanguageLabel-sc-1ya9m5e-1 eNlqpi' and text()='LCS Spring 2020']"))).click()
except:
    driver.refresh()
    frame = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
    driver.switch_to.frame(frame)

time.sleep(1)
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//span[@class='OptionsMenu__Text-h4phwe-4 dDkXYG' and text()='LCS Summer 2019']"))).click()
time.sleep(1)
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='RiotVODs__SelectedLanguageLabel-sc-1ya9m5e-1 eNlqpi' and text()='LCS Summer 2019']"))).click()

SCROLL_PAUSE_TIME = 1


last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.XPATH, "//span[@class='ladda-label' and text()='Load more']"))).click()
        except:
            break
    last_height = new_height


schedule = WebDriverWait(driver, 7).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'game-selector__games__link')))
games = []
for x, week in enumerate(schedule):
    week_games = driver.find_elements_by_class_name('riot-match-item')
    for game in week_games:
        games.insert(0, [x, game])
