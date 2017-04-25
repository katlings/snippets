#!/usr/bin/env python

"""
Given a file with a list of song/artist search terms and Google Music
credentials, make a new playlist and add each song to it.
"""

from functools import wraps

import argparse
import simplejson as json

from gmusicapi import Mobileclient


# http://stackoverflow.com/questions/1988804/what-is-memoization-and-how-can-i-use-it-in-python
def memoize(fn):
    """returns a memoized version of any function that can be called
    with the same list of arguments.
    Usage: foo = memoize(foo)"""

    def handle_item(x):
        if isinstance(x, dict):
            return make_tuple(sorted(x.items()))
        elif hasattr(x, '__iter__'):
            return make_tuple(x)
        else:
            return x

    def make_tuple(L):
        return tuple(handle_item(x) for x in L)

    @wraps(fn)
    def foo(*args, **kwargs):
        items_cache = make_tuple(sorted(kwargs.items()))
        args_cache = make_tuple(args)
        if (args_cache, items_cache) not in foo.past_calls:
            foo.past_calls[(args_cache, items_cache)] = fn(*args,**kwargs)
        return foo.past_calls[(args_cache, items_cache)]

    foo.past_calls = {}
    foo.__name__ = 'memoized_' + fn.__name__
    return foo


class PlaylistMaker(object):
    def __init__(self, dry_run=False):
        self.api = Mobileclient()
        self.live = not dry_run

        with open('creds.json') as f:
            creds = json.loads(f.read())

        self.logged_in = self.api.login(creds['username'], creds['password'], Mobileclient.FROM_MAC_ADDRESS)

    def make_playlist(self, name):
        return self.api.create_playlist(name, public=True) if self.live else "dry-run-no-playlist"

    def find_song_ids(self, songs, strict_match=False):
        song_ids = []
        not_found_songs = []
        
        for song in songs:
            result = self.api.search(song)
            try:
                song_hits = result.get('song_hits', [])
                if strict_match:
                    hits = [x['track'] for x in song_hits if x['track']['title'].lower() == song.lower()]
                    hit = hits[0]
                else:
                    hit = song_hits[0]['track']
                song_ids.append(hit['storeId'])
                print "Adding: ", hit['title'], "-", hit['artist']
            except IndexError, KeyError:
                not_found_songs.append(song)
                print "Could not find a result for: ", song
                return []

        if not_found_songs:
            print 'Songs not found:'
            print '\n'.join(not_found_songs)

        return song_ids

    def populate_playlist(self, playlist_id, song_ids):
        if self.live:
            self.api.add_songs_to_playlist(playlist_id, song_ids)
            print "Added {} songs to playlist".format(len(song_ids))
        else:
            print "Not adding {} songs to playlist".format(len(song_ids))

    def sentence_to_song_ids(self, sentence):
        return self.words_to_song_ids([w.lower() for w in sentence.split()])

    @memoize
    def words_to_song_ids(self, words):
        def song_exists(title):
            return self.find_song_ids([title], strict_match=True)

        use_or_lose = []
        for i, word in enumerate(words):
            use_or_lose.append(word)
            song_ids = song_exists(' '.join(use_or_lose))
            if song_ids:
#                print "found a song called {}".format(" ".join(use_or_lose))

                if len(use_or_lose) == len(words):
                    return song_ids
                else:
                    results = self.words_to_song_ids(words[i+1:])
                    if results is None:
                        return None
                    return song_ids + self.words_to_song_ids(words[i+1:])



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
    sids = pm.find_song_ids(songartists)
    pm.populate_playlist(pid, sids)
    pm.api.logout()


if __name__ == "__main__":
    main()
