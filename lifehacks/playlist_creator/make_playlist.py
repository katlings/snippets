#!/usr/bin/env python

"""
Given a file with a list of song/artist search terms and Google Music
credentials, make a new playlist and add each song to it.
"""

import argparse
import simplejson as json

from gmusicapi import Mobileclient


class PlaylistMaker(object):
    def __init__(self, dry_run=False):
        self.api = Mobileclient()
        self.live = not dry_run

        with open('creds.json') as f:
            creds = json.loads(f.read())

        self.logged_in = self.api.login(creds['username'], creds['password'], Mobileclient.FROM_MAC_ADDRESS)

    def make_playlist(self, name):
        return self.api.create_playlist(name, public=True) if self.live else "dry-run-no-playlist"

    def populate_playlist(self, playlist_id, songs):
        song_ids = []
        not_found_songs = []
        
        for song in songs:
            result = self.api.search(song)
            try:
                hit = result.get('song_hits')[0]['track']
                song_ids.append(hit['storeId'])
                print "Adding: ", hit['title'], "-", hit['artist']
            except IndexError, KeyError:
                not_found_songs.append(song)
                print "Could not find a result for: ", song

        if self.live:
            self.api.add_songs_to_playlist(playlist_id, song_ids)
            print "Added {} songs to playlist".format(len(song_ids))

        print 'Songs not found:'
        print '\n'.join(not_found_songs)


def main():
    parser = argparse.ArgumentParser(description='Make a playlist and populate with songs. Store credentials in creds.json with format {"username": username, "password": password}')
    parser.add_argument('--filename', '-f', required=True, help='Text file full of search terms. One song per line will be added to the playlist')
    parser.add_argument('--name', '-n', help='Name of the playlist. Defaults to the filename')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Just print search results; don\'t actually create a playlist or add songs to it')
    args = parser.parse_args()

    playlist_name = args.name or args.filename

    with open(args.filename) as f:
        songartists = f.readlines()

    pm = PlaylistMaker(args.dry_run)
    pid = pm.make_playlist(playlist_name)
    pm.populate_playlist(pid, songartists)
    pm.api.logout()


if __name__ == "__main__":
    main()
