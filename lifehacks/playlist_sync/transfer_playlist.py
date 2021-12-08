#!/usr/bin/env python3

import json
import re

import click
from fuzzywuzzy import fuzz
from gmusicapi import Mobileclient
import spotipy
from spotipy.oauth2 import SpotifyOAuth

gapi = Mobileclient()

@click.command()
@click.argument('playlist-id')
@click.option('--test', is_flag=True)
def transfer_playlist(playlist_id, test):
    if not gapi.oauth_login(Mobileclient.FROM_MAC_ADDRESS):
        print('Could not log in to Google Music; have you performed oauth setup?')
        print('See https://unofficial-google-music-api.readthedocs.io/en/latest/reference/mobileclient.html#setup-and-login')
        return
    try:
        with open('creds.json') as f:
            creds = json.loads(f.read())
    except FileNotFoundError:
        print('Could not find Spotify credentials; they should be in creds.json')

    spauth = SpotifyOAuth(client_id=creds['spotify_client_id'], client_secret=creds['spotify_client_secret'], scope='playlist-modify-private', redirect_uri='http://katlings.net')
    spapi = spotipy.Spotify(auth_manager=spauth)
    spuser = spapi.me()['id']

    print('Fetching Google playlist data....')
    playlists = gapi.get_all_user_playlist_contents()
    chosen_playlist = [p for p in playlists if p['id'] == playlist_id]
    if not chosen_playlist:
        print('Could not find that playlist ID')
        return
    chosen_playlist = chosen_playlist[0]

    print(f'Transferring playlist "{chosen_playlist["name"]}"')

    tracks = []
    for track in chosen_playlist['tracks']:
        if not 'track' in track:
            print(f"No track data for track {track['id']}")
        else:
            # dump parentheticals; we just want searchable title and artist
            clean_title = re.sub(r'\[[^)]*\]', '', re.sub(r'\([^)]*\)', '', track['track']['title'])).split('-')[0].strip()
            clean_artist = re.sub(r'\[[^)]*\]', '', re.sub(r'\([^)]*\)', '', track['track']['artist'])).split('-')[0].strip()
            tracks.append(f"{clean_title} {clean_artist}")

    if test:
        print(f'Test; not adding {len(tracks)} tracks to a new Spotify playlist')
        for track in tracks:
            print(track)
    else:
        spplaylist = spapi.user_playlist_create(spuser, chosen_playlist['name'])
        sptrack_ids = []
        for track in tracks:
            result = spapi.search(track, limit=1, type='track')
            try:
                sptrack_ids.append(result['tracks']['items'][0]['id'])
            except (KeyError, IndexError):
                print(f'Could not find track "{track}"; skipping')

            if len(sptrack_ids) >= 99:
                spapi.playlist_add_items(spplaylist['id'], sptrack_ids)
                sptrack_ids = []

        if sptrack_ids:
            spapi.playlist_add_items(spplaylist['id'], sptrack_ids)

if __name__ == '__main__':
    transfer_playlist()
