#!/usr/bin/env python

"""
Given a file with a list of song/artist search terms and Google Music
credentials, make a new playlist and add each song to it.
"""

from functools import wraps
import re

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
    def __init__(self, dry_run=False, verbose=False):
        self.api = Mobileclient()
        self.live = not dry_run
        self.verbose = verbose

        with open('creds.json') as f:
            creds = json.loads(f.read())

        self.logged_in = self.api.login(creds['username'], creds['password'], Mobileclient.FROM_MAC_ADDRESS)

    def make_playlist(self, name):
        pid = self.api.create_playlist(name, public=True) if self.live else 'dry-run-no-playlist'
        if self.verbose:
            print 'Created playlist with id: {}'.format(pid)
        return pid

    def find_song_ids(self, songs, strict_match=False):
        song_ids = []
        not_found_songs = []
        
        for song in songs:
            result = self.api.search(song)
            try:
                song_hits = result.get('song_hits', [])
                if strict_match:
                    hits = [x['track'] for x in song_hits if re.sub(r'[^a-z ]+', '', x['track']['title'].lower()) == song.lower()]
                    hit = hits[0]
                else:
                    hit = song_hits[0]['track']
                song_ids.append(hit['storeId'])

                if self.verbose:
                    print 'Adding: ', hit['title'], '-', hit['artist']
            except IndexError, KeyError:
                not_found_songs.append(song)
                if self.verbose:
                    print 'Could not find a result for: ', song

        if self.verbose and not_found_songs:
            print 'Songs not found:'
            print '\n'.join(not_found_songs)

        return song_ids

    def populate_playlist(self, playlist_id, song_ids):
        if self.live and song_ids:
            self.api.add_songs_to_playlist(playlist_id, song_ids)
            print 'Added {} songs to playlist'.format(len(song_ids))
        elif not song_ids:
            print 'No songs to add to playlist'
        else:
            print 'Not adding {} songs to playlist'.format(len(song_ids))

    def sentence_to_song_ids(self, sentence):
        result = self.words_to_song_ids([re.sub(r'[^a-z ]+', '', w.lower()) for w in sentence.split()])
        if not result:
            print 'Could not find a song arrangement for sentence: {}'.format(sentence)
        return result

    @memoize
    def words_to_song_ids(self, words):
        def song_exists(title):
            return self.find_song_ids([title], strict_match=True)

        if words == []:
            return words

        for i in xrange(len(words), 0, -1):
            temp_sentence = ' '.join(words[:i])

            song_id = song_exists(temp_sentence)

            if song_id:
                rest = self.words_to_song_ids(words[i:])

                if rest is not None:
                    return song_id + rest


def main():
    parser = argparse.ArgumentParser(description='Make a playlist and populate with songs. Store credentials in creds.json with format {"username": username, "password": password}')
    parser.add_argument('--filename', '-f', help='Text file full of search terms. One song per line will be added to the playlist')
    parser.add_argument('--name', '-n', help='Name of the playlist. Defaults to the filename')
    parser.add_argument('--sentence', '-s', help='A sentence to write out using song names')
    parser.add_argument('--playlist-id', '-p', help='Use this playlist (by id) instead of creating a new one')
    parser.add_argument('--dry-run', '-d', action='store_true', help="Just print search results; don't actually create a playlist or add songs to it")
    parser.add_argument('--verbose', '-v', action='store_true', help='Print search information')
    args = parser.parse_args()

    playlist_name = args.name or args.filename

    pm = PlaylistMaker(args.dry_run, args.verbose)

    if args.playlist_id:
        pid = args.playlist_id
    else:
        pid = pm.make_playlist(playlist_name)

    if args.filename:
        with open(args.filename) as f:
            songartists = f.readlines()
        sids = pm.find_song_ids(songartists)
    elif args.sentence:
        sids = pm.sentence_to_song_ids(args.sentence)

    pm.populate_playlist(pid, sids)
    pm.api.logout()


if __name__ == '__main__':
    main()
