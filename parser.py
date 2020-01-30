import numpy as np

titles = ['Game Time', 'Name', 'Champ', 'Role', 'Kills', 'Deaths', 'Assists', 'Gold Earned', 'CS',
          'Kill Participation', 'Champ Damage Share', 'Wards Placed', 'Wards Destroyed', 'Attack Damage',
          'Ability Power', 'Critical Chance', 'Attack Speed', 'Life Steal', 'Armor', 'Magic Resist', 'Tenacity',
          'Dragons', 'Inhibitors', 'Barons', 'Towers']

def parse_text(payload, game_time):
    #TODO parse dragons, towers, etc.
    values = [0] * len(titles)
    values[0] = game_time
    for n in range(len(payload)):
        if n == 0:
            name, champ_role, _ = payload[n].text.split('\n')
            team = name.split(' ')[0]
            champ, role = champ_role.split('–')
            values[1] = name
            values[2] = champ
            values[3] = role
        elif n == 1:
            stat_split = payload[n].text.split('\n')
            kill, death, assist = stat_split.pop(0).split(' / ')
            values[4] = kill
            values[5] = death
            values[6] = assist
            enter = 0
            for index, stat in enumerate(stat_split):
                if index % 2 != 0:
                    values[enter + 7] = stat
                    enter +=1
        elif n == 2:
            attr_split = payload[n].text.split('\n')
            enter = 0
            for index, stat in enumerate(attr_split):
                if index % 2 == 0:
                    values[enter + 13] = stat
                    enter +=1
    return titles, values, team


def parse_team(team_stats, dragons, game_time, blue_team, red_team):
    blue_team_values = [0] * len(titles)
    blue_team_values[0] = game_time
    blue_team_values[1] = blue_team
    red_team_values = [0] * len(titles)
    red_team_values[0] = game_time
    red_team_values[1] = red_team
    all_dragon = dragons.split('DRAGONS')
    blue_drag, red_drag = all_dragon[0].count("dragon "), all_dragon[1].count("dragon ")
    blue_team_values[-4] = blue_drag
    red_team_values[-4] = red_drag
    input = team_stats[0].text.split('\n')[4:]

    for n in range(1, 3):
        blue_team_values[-n]: input[n+3]


    for n in range(1, 3):
        red_team_values[-n]: input[n+5]

    return red_team_values, blue_team_values
