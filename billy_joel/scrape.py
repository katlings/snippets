#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests


STATES = ['Alabama',
'Alaska',
'Arizona',
'Arkansas',
'California',
'Colorado',
'Connecticut',
'Delaware',
'Florida',
'Georgia',
'Hawaii',
'Idaho',
'Illinois',
'Indiana',
'Iowa',
'Kansas',
'Kentucky',
'Louisiana',
'Maine',
'Maryland',
'Massachusetts',
'Michigan',
'Minnesota',
'Mississippi',
'Missouri',
'Montana',
'Nebraska',
'Nevada',
'New Hampshire',
'New Jersey',
'New Mexico',
'New York',
'North Carolina',
'North Dakota',
'Ohio',
'Oklahoma',
'Oregon',
'Pennsylvania',
'Rhode',
'Island',
'South Carolina',
'South Dakota',
'Tennessee',
'Texas',
'Utah',
'Vermont',
'Virginia',
'Washington',
'West Virginia',
'Wisconsin',
'Wyoming']


def filter_versions(song, artist_id):
    return song['primary_artist']['id'] == artist_id and \
            ' live' not in song['title'].lower() and \
            'remastered' not in song['title'].lower() and \
            'remix' not in song['title'].lower() and \
            'radio edit' not in song['title'].lower() and \
            'tribute' not in song['title'].lower() and \
            'tracklist' not in song['title'].lower() and \
            'version' not in song['title'].lower()


def collect_lyrics(url):
    bs = BeautifulSoup(requests.get(url).content, 'html.parser')
    lyrics = bs.find(attrs={'class': 'lyrics'}).text
    return lyrics


def contains_state(lyrics):
    for state in STATES:
        if state in lyrics:
            return True
    return False


def main():
    artist_id = 586  # The Beatles
    artist_id = 1138  # The Beach Boys
    artist_id = 16965  # Billy Joel
    artist_id = 560  # Elton John
    artist_id = 181  # Bob Dylan
    url = f'https://genius.com/api/artists/{artist_id}/songs'
    page = 1
    songs = []

    while page:
        print('Fetching page', page)
        response = requests.get(url, params={'page': page})
        data = response.json()['response']
        songs.extend([(s['title'], s['url']) for s in data['songs'] if filter_versions(s, artist_id)])
        page = data.get('next_page')

    lyrics = {}

    for i, (song, url) in enumerate(songs):
        print(f'Fetching lyrics for {i+1}/{len(songs)}')
        lyrics[song] = collect_lyrics(url)

    cs = 0
    for song in lyrics:
        if contains_state(lyrics[song]):
            cs += 1
            print(song)
    print(cs, '/', len(lyrics), ',', cs/len(lyrics))

if __name__ == '__main__':
    main()
