#!/usr/bin/env python

"""
Rank 2016 March Madness teams by average player height to generate a bracket
"""

from bs4 import BeautifulSoup
import re
import requests


def ncaa():
    def transform_team(s):
        return re.sub(r'[^a-zA-Z\-]', '', s.lower().replace(' ', '-'))
    
    def to_inches(s):
        feet, inches = s.split('-')
        return int(feet)*12 + int(inches)

    ncaa = 'http://www.ncaa.com'
    
    bs = BeautifulSoup(requests.get(ncaa + '/news/basketball-men/bracket-beat/2016-03-14/march-madness-every-team-ranked-ncaas-complete-seed-list').content, 'html.parser')
    teams = bs.find_all('p')
    #print teams
    teams = filter(lambda x: x is not None, map(lambda t: re.match(r'\d+\. (?P<team>.*)', t.getText()), teams))
    assert len(teams) == 68

    heights = []

    subs = {
        'little-rock': 'ualr',
        'uncw': 'unc-wilmington',
        'csu-bakersfield': 'bakersfield',
    }

    for team in teams:
        #print team.group('team')
        t = transform_team(team.group('team'))
        #print t

        if t in subs:
            t = subs[t]
    
        sbs = BeautifulSoup(requests.get(ncaa + '/schools/%s/basketball-men#tabs-2' % t).content, 'html.parser')
        players = sbs.find_all('table', class_='ncaa-schools-sport-table')[1].findChildren('tr')[1:]
        #print len(players)
        num_players = len(players)
        
        height = 0
        for row in players:
            try:
                height += to_inches(row.find_all('td')[3].text)
            except ValueError:
                num_players -= 1
                continue

        #print num_players
        #print height

        heights.append((height*1.0/num_players, t))
        #print heights

    #print sorted(heights)
    for i, hs in enumerate(reversed(sorted(heights))):
        h, s = hs
        print i+1, s, h


if __name__ == "__main__":
    ncaa()
