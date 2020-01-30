import requests


def champions():
    champion_list = {}
    patch = '9.13.1'
    url = f'http://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json'
    payload = requests.get(url)
    payload = payload.json()
    for champion in payload['data'].keys():
        key = payload['data'][champion]['key']
        champion_list[champion] = key
    return champion_list


def regions():
    regions_dict = {'Brazil': 'BR1',
                    'Europe Nordic and East': 'EUN1',
                    'Europe West': 'EUW1',
                    'Japan': 'JP1',
                    'Korea': 'KR',
                    'Latin America 1': 'LA1',
                    'Latin America 2': 'LA2',
                    'North America': 'NA1',
                    'Oceania': 'OC1',
                    'Turkey': 'TR1',
                    'Russia': 'RU'
                    }
    return regions_dict


def queue_code():
    queue_list = {}
    url = f'http://static.developer.riotgames.com/docs/lol/queues.json'
    payload = requests.get(url)
    payload = payload.json()
    for i in range(len(payload)):
        queue_list[payload[i]['description']] = payload[i]['queueId']
    return queue_list
