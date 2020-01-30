from riotwatcher import RiotWatcher, ApiError
import json
import Champions
import pandas as pd

api_key = 'RGAPI-3b3cf6a1-945c-4b26-ad43-cc51b96ff21a'
watcher = RiotWatcher(api_key)
champion_dict = Champions.champions()
regions_dict = Champions.regions()

regions = []
for region in regions_dict.values():
    regions.append(region)

in_file = pd.read_excel('DKSalaries.xlsx', header=1)
contestants = []
for name in in_file['Name']:
    contestants.append(str(name).lstrip())

df = pd.read_excel('master_file.xlsx')
for contestant in contestants:
    data = df.loc[df['player'] == contestant]

my_region = regions_dict['North America']
me = watcher.summoner.by_name(my_region, 'jensen')


matches = watcher.match.matchlist_by_account(my_region, me['accountId'])
match = matches['matches'][0]['gameId']
print(me)
print(match)
# game = watcher.match.by_id(my_region, match)

# output = json.dumps(game, indent=4, sort_keys=True)
# print(output)


