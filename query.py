import mwclient
import pandas as pd


def api():
    # this function gets game results from api. attaches results to schedule joined on "path"
    site = mwclient.Site('lol.gamepedia.com', path='/')
    page_to_query = "Data:LCS/2020 Season/Spring Season"
    response = site.api('cargoquery',
                        limit='max',
                        tables="MatchScheduleGame=MSG,MatchSchedule=MS",
                        fields="MSG.Blue, MSG.Red, MSG.Winner, MSG.GameID_Wiki, MSG.UniqueMatch",
                        where=r'MSG._pageName="%s" AND MSG.MatchHistory IS NOT NULL AND NOT MSG.MatchHistory RLIKE ".*(lpl|lol)\.qq\.com.*"' % page_to_query,
                        join_on="MSG.UniqueMatch=MS.UniqueMatch",
                        order_by="MS.N_Page,MS.N_MatchInPage, MSG.N_GameInMatch"
                        )
    games = []
    for i in range(len(response['cargoquery'])):
        blue = response['cargoquery'][i]['title']['Blue']
        red = response['cargoquery'][i]['title']['Red']
        result = response['cargoquery'][i]['title']['Winner']
        title = response['cargoquery'][i]['title']['GameID Wiki']
        games.append([blue, red, result, title])
    df = pd.DataFrame(games)
    summer = pd.read_excel('summer_results.xlsx')
    df = pd.concat([df, summer], axis=0)

    schedule = pd.read_excel('schedule.xlsx')
    schedule = pd.Series(schedule[1])
    schedule = schedule[:-5]
    df = df.reset_index(drop=True)
    schedule = schedule.reset_index(drop=True)
    df = pd.concat([df, schedule], axis=1)
    df.columns = [0, 1, 'result', 3, 'path']
    df.to_excel('results.xlsx', index=False)

api()