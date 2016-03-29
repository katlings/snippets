#!/usr/bin/env python

"""
Rank NFL teams by weight to generate a bracket for the season
"""

from bs4 import BeautifulSoup
import re
import requests

def espn():
    espn = 'http://espn.go.com'
    teams = []

    bs = BeautifulSoup(requests.get(espn + '/nfl/players').content, "html.parser")
    for link in bs.find_all('a'):
        if 'roster' in link.get('href'):
            #print espn + link.get('href')
            team = link.get('href').split('/')[-1]
            weight = 0
            bs2 = BeautifulSoup(requests.get(espn + link.get('href')).content, "html.parser")
            players = bs2.find_all('tr', class_='evenrow') + bs2.find_all('tr', class_='oddrow')
            for row in players:
                weight += int(row.find_all('td')[5].text)
            teams.append((weight, team, len(players)))

    print sorted(teams)

def nfl():
    nfl = 'http://www.nfl.com'
    teams = []

    bs = BeautifulSoup(requests.get(nfl + '/teams').content, "html.parser")
    team_info = bs.find_all('div', class_='teamslandinggridgroup')
    for team in team_info:
        roster_url = team.find('option', value=re.compile('roster')).get('value')
        #print nfl + roster_url
        teamname = roster_url.split('/')[2]
        weight = 0
        num_players = 0

        bs2 = BeautifulSoup(requests.get(nfl + roster_url).content, "html.parser")
        players = bs2.find_all('tr', class_='even') + bs2.find_all('tr', class_='odd')
        for row in players:
            if row.find_all('td')[3].text == "ACT":
                weight += int(row.find_all('td')[5].text)
                num_players += 1
        teams.append((weight, teamname, num_players))

    for i, rank in enumerate(reversed(sorted(teams))):
        weight, team, _ = rank
        print i+1, team, weight


if __name__ == "__main__":
    nfl()
