#!/usr/bin/env python3

import json
import re

import click
import spotipy
from spotipy.oauth2 import SpotifyOAuth


@click.command()
@click.argument('search_string')
def search_playlists(search_string):
    try:
        with open('creds.json') as f:
            creds = json.loads(f.read())
    except FileNotFoundError:
        print('Could not find Spotify credentials; they should be in creds.json')

    spauth = SpotifyOAuth(client_id=creds['spotify_client_id'], client_secret=creds['spotify_client_secret'], scope='playlist-read-private', redirect_uri='https://katlings.net')
    spapi = spotipy.Spotify(auth_manager=spauth)
    spuser = spapi.me()['id']

    playlists = []
    result = spapi.current_user_playlists()
    playlists.extend(result['items'])
    while result['next']:
        m = re.match(r'.*offset=(\d+)&limit=(\d+).*', result['next'])
        offset, limit = int(m.group(1)), int(m.group(2))
        result = spapi.current_user_playlists(limit=limit, offset=offset)
        playlists.extend(result['items'])
    print(f'{len(playlists)} playlists found.')

    matching_playlists = []

    for playlist in playlists:
        pid = playlist['id']
        tracks = []
        result = spapi.playlist_items(pid)
        tracks.extend(result['items'])
        while result['next']:
            m = re.match(r'.*offset=(\d+)&limit=(\d+).*', result['next'])
            offset, limit = int(m.group(1)), int(m.group(2))
            result = spapi.playlist_items(pid, limit=limit, offset=offset)
            tracks.extend(result['items'])
        #print(f'{len(tracks)} tracks found in playlist {playlist["name"]}')

        for i, track in enumerate(tracks):
            try:
                if search_string.lower() in track['track']['name'].lower() or \
                   any(search_string.lower() in artist['name'].lower() for artist in track['track']['artists']): 
                    print(f'{i+1}/{len(tracks)}: playlist {playlist["name"]} contains song {track["track"]["name"]} by {",".join(artist["name"] for artist in track["track"]["artists"])}')
            except (TypeError, KeyError):
                continue


        

if __name__ == '__main__':
    search_playlists()
