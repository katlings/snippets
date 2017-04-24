#!/usr/bin/env python

"""
Given a file with a list of song/artist search terms and Google Music
credentials, make a new playlist and add each song to it.
"""

import argparse
import simplejson as json

from gmusicapi import Mobileclient


class PlaylistMaker(object):
    def __init__(self):
        self.api = Mobileclient()

        with open('creds.json') as f:
            creds = json.loads(f.read())

        self.logged_in = self.api.login(creds['username'], creds['password'], Mobileclient.FROM_MAC_ADDRESS)

    def make_playlist(self, name):
        return self.api.create_playlist(name, public=True)

    def populate_playlist(self, playlist_id, songs):
        song_ids = []
        
        for song in songs:
            result = self.api.search(song)
            hit = result.get('song_hits')[0]['track']
            print "Adding: ", hit['title'], " - ", hit['artist']
            song_ids.append(hit['storeId'])

        self.api.add_songs_to_playlist(playlist_id, song_ids)


def main():
    parser = argparse.ArgumentParser(description='Make a playlist and populate with songs. Store credentials in creds.json with format {"username": username, "password": password}')
    parser.add_argument('--filename', '-f', required=True, help='Text file full of search terms. One song per line will be added to the playlist')
    parser.add_argument('--name', '-n', help='Name of the playlist. Defaults to the filename')
    args = parser.parse_args()

    playlist_name = args.name or args.filename

    with open(args.filename) as f:
        songartists = f.readlines()

    pm = PlaylistMaker()
    pid = pm.make_playlist(playlist_name)
    pm.populate_playlist(pid, songartists)
    pm.api.logout()


if __name__ == "__main__":
    main()
