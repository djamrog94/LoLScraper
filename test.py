def parse(input_data):
    blue_team = {}
    red_team = {}

    payload = input_data
    time = payload[0]

    for x in range(1, 10, 2):
        count = 0
        data = payload[x].split('\n')
        b_name = data[1]
        r_name = data[8]
        for team in ['blue', 'red']:
            for obj in ['name', 'role', 'health', 'mana', 'AD', 'AP']:
                if count in [0, 7]:
                    if team == 'blue':
                        count += 1
                        blue_team[data[count]] = {}
                    else:
                        count += 1
                        red_team[data[count]] = {}
                elif count in [2, 9]:
                    if team == 'blue':
                        blue_team[b_name]['role'] = data[count].split(' - ')[0]
                        blue_team[b_name]['champ'] = data[count].split(' - ')[1]
                    else:
                        red_team[r_name]['role'] = data[count].split(' - ')[0]
                        red_team[r_name]['champ'] = data[count].split(' - ')[1]

                else:
                    if team == 'blue':
                        blue_team[b_name][f'{obj}'] = data[count]
                    else:
                        red_team[r_name][f'{obj}'] = data[count]
                count += 1

        attr = payload[x + 1].split('\n')
        for n in range(len(attr)):
            if n in [0, 24]:
                if n == 0:
                    kills, deaths, assists = attr[n].split((' / '))
                    k, d, a = attr[n + 1].split((' / '))
                    kda = dict(zip([k, d, a], [kills, deaths, assists]))
                    for key in kda:
                        blue_team[b_name][key] = kda[key]
                else:
                    kills, deaths, assists = attr[n].split((' / '))
                    k, d, a = attr[n + 1].split((' / '))
                    kda = dict(zip([k, d, a], [kills, deaths, assists]))
                    for key in kda:
                        red_team[r_name][key] = kda[key]

            else:
                if n % 2 == 0:
                    if n < 24:
                        blue_team[b_name][attr[n + 1]] = attr[n]
                    else:
                        red_team[r_name][attr[n + 1]] = attr[n]

    team_data = payload[11].split('\n')
    b_team_name = team_data[14].split(' ')[0]
    r_team_name = team_data[19].split(' ')[0]
    blue_team[b_team_name] = {}
    red_team[r_team_name] = {}
    for index, team in enumerate(['blue', 'red']):
        for index1, tag in enumerate(['Inhibitors', 'Barons', 'Towers', 'Kills']):
            if tag == 'Kills':
                value = team_data[index1 + 5 + (index * 5)]
            else:
                value = team_data[index1 + 4 + (index * 5)]
            if team == 'blue':
                blue_team[b_team_name][tag] = value
            else:
                red_team[r_team_name][tag] = value

    blue_team['Dragons'] = payload[12]
    red_team['Dragons'] = payload[13]

    return time, blue_team, red_team


