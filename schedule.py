from driver import *
import pandas as pd

with open('cred.txt', 'r') as f:
    user = f.readline().rstrip()
    pw = f.readline().rstrip()

def main():
    choices = {1: schedule, 2: check_schedule}
    print('What would you like to do? ')
    print('1: Update schedule?')
    print('2: Check completed games? ')
    choice = int(input(''))
    while choice not in choices:
        choice = int(input('Try again.\n'))
    if choice == 1:
        schedule()
    else:
        check_schedule()


def schedule():
    # start webdriver and navigate to VoD page
    driver = init()

    driver.get('https://watch.lolesports.com')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//a[@class='riotbar-anonymous-link riotbar-account-action']"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys(user)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(pw)
    driver.find_elements_by_tag_name("button")[1].click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "title-text"))).click()
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "proViewVods"))).click()
    frame = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "znipe-iframe")))
    driver.switch_to.frame(frame)
    time.sleep(3)

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

    # find games in the spring 2020 split
    lcs_spring = find_game(driver)
    spring_schedule = WebDriverWait(driver, 7).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'matches-date-wrapper')))
    for i in range(len(lcs_spring)):
        matchup = lcs_spring[i][1].text.split('\nVS\n')
        season = spring_schedule[lcs_spring[i][0]].text.split('\n')[0].replace(' ', '_')
        file_name = "_".join(matchup) + '_' + season
        lcs_spring[i][1] = file_name

    # navigate to the summer 2019 split page
    while True:
        try:
            time.sleep(3)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='RiotVODs']"))).click()
            time.sleep(1)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'LCS Summer 2019')]"))).click()
            time.sleep(1)
            driver.find_element_by_css_selector("div[class^='RiotVODs']").click()
            break
        except:
            driver.refresh()

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

    # find games in the summer 2019 split
    lcs_summer = find_game(driver)
    summer_schedule = WebDriverWait(driver, 7).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, 'matches-date-wrapper')))
    for i in range(len(lcs_summer)):
        matchup = lcs_summer[i][1].text.split('\nVS\n')
        season = summer_schedule[lcs_summer[i][0]].text.split('\n')[0].replace(' ', '_')
        file_name = "_".join(matchup) + '_' + season
        lcs_summer[i][1] = file_name

    # create data frame of all games available
    spring_df = pd.DataFrame(lcs_spring)
    spring_df.reset_index(inplace=True)
    summer_df = pd.DataFrame(lcs_summer)
    summer_df.reset_index(inplace=True)

    # save this df to schedule.xlsx
    all_games = spring_df.append(summer_df)
    all_games.to_excel('schedule.xlsx', index=False)


def check_schedule():
    # read df that was saved from the schedule function
    schedule = pd.read_excel('schedule.xlsx')

    # check final folder to see games that have been properly parsed
    games = os.listdir('data/final')
    games = [x[:-5] for x in games]

    # tracks how many games were completed last time function was run
    with open('schedule.txt', 'r') as f:
        number = int(f.readline())
    count = 0
    schedule[2] = ''
    # place an x on the df next to completed games
    for n in range(len(schedule)):
        if schedule.iloc[n][1] in games:
            schedule[2][n] = 'X'
            count += 1
    new_number = count - number
    percent = count / len(schedule) * 100

    # print the number of games completed, the percentage of games completed, and how many completed since last run
    print(f'{count} / {len(schedule)}. {percent:.1f} Added {new_number} games since last check.')
    with open('schedule.txt', 'w') as f:
        f.write(str(count))

    # check how many games are saved in review folder
    folders = os.listdir('data/review')
    folders = [x[:-5] for x in folders]
    schedule[3] = ''
    for n in range(len(schedule)):
        if schedule.iloc[n][1] in folders:
            schedule[3][n] = 'X'

    # saves df back to schedule.xlsx
    schedule.to_excel('schedule.xlsx', index=False)


if __name__ == '__main__':
    main()
