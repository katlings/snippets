#!/usr/bin/env python3

import json
import re

import click
import spotipy
from spotipy.oauth2 import SpotifyOAuth

@click.command()
@click.argument('filename')
@click.option('--dry-run', is_flag=True)
def create_playlist(filename, dry_run):
    try:
        with open('creds.json') as f:
            creds = json.loads(f.read())
    except FileNotFoundError:
        print('Could not find Spotify credentials; they should be in creds.json')

    spauth = SpotifyOAuth(client_id=creds['spotify_client_id'], client_secret=creds['spotify_client_secret'], scope='playlist-modify-private', redirect_uri='https://katlings.net')
    spapi = spotipy.Spotify(auth_manager=spauth)
    spuser = spapi.me()['id']

    if not dry_run:
        playlist_name = input('What to call this playlist: ')

    try:
        with open(filename) as f:
            tracks = f.readlines()
    except FileNotFoundError:
        print(f'Could not open file {filename}')

    if not dry_run:
        spplaylist = spapi.user_playlist_create(spuser, playlist_name, public=False)

    sptrack_ids = []
    skipped_tracks = []

    for track in tracks:
        track = track.strip()
        if not track or track.startswith('#'):
            continue
        
        track = ' '.join(track.split(' - '))

        result = spapi.search(track, limit=1, type='track')
        try:
            match = result['tracks']['items'][0]
            sptrack_ids.append(match['id'])
            if dry_run:
                artists = ','.join(a['name'] for a in match['album']['artists'])
                title = match['name']
                print(f'Found track "{track}": {artists} - {title}')
        except (KeyError, IndexError):
            skipped_tracks.append(track)
            print(f'Could not find track "{track}"; skipping')

        if not dry_run and len(sptrack_ids) >= 99:
            spapi.playlist_add_items(spplaylist['id'], sptrack_ids)
            sptrack_ids = []

    if not dry_run and sptrack_ids:
        spapi.playlist_add_items(spplaylist['id'], sptrack_ids)

    print(f'Skipped {len(skipped_tracks)} tracks:')
    for track in skipped_tracks:
        print(track)

if __name__ == '__main__':
    create_playlist()
