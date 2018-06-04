#!/usr/bin/env python3

"""
Given a file with a list of song/artist search terms and Google Music
credentials, make a new playlist and add each song to it.
"""

from functools import wraps
import re

import click
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


def alphanum(s):
    return re.sub(r'[^a-z0-9]+', '', s.lower())


class PlaylistMaker(object):
    def __init__(self, dry_run=False, verbose=0):
        self.api = Mobileclient()
        self.live = not dry_run
        self.verbose = verbose
        self.playlists = None

        with open('creds.json') as f:
            creds = json.loads(f.read())

        self.logged_in = self.api.login(creds['username'], creds['password'], Mobileclient.FROM_MAC_ADDRESS)

    def make_playlist(self, name):
        pid = self.api.create_playlist(name, public=True) if self.live else 'dry-run-no-playlist'
        if self.verbose:
            print('Created playlist with id: {}'.format(pid))
        return pid

    def find_song_ids(self, songs, strict_match=False):
        song_ids = []
        not_found_songs = []
        
        for song in songs:
            result = self.api.search(song)
            try:
                song_hits = result.get('song_hits', [])
                if strict_match:
                    hits = [x['track'] for x in song_hits if alphanum(x['track']['title']) == alphanum(song)]
                    hit = hits[0]
                else:
                    hit = song_hits[0]['track']
                song_ids.append(hit['storeId'])

                if self.verbose > 1:
                    print('Adding: ', hit['title'], '-', hit['artist'])
            except (IndexError, KeyError):
                not_found_songs.append(song)
                if self.verbose > 1:
                    print('Could not find a result for:', song)
                return []

        if self.verbose and not_found_songs:
            print('Songs not found:')
            print('\n'.join(not_found_songs))

        return song_ids

    def populate_playlist(self, playlist_id, song_ids):
        if self.live and song_ids:
            self.api.add_songs_to_playlist(playlist_id, song_ids)
            print('Added {} songs to playlist'.format(len(song_ids)))
        elif not song_ids:
            print('No songs to add to playlist')
        else:
            print('Not adding {} songs to playlist'.format(len(song_ids)))

    def sentence_to_song_ids(self, sentence):
        result = self.words_to_song_ids([alphanum(w) for w in sentence.split()])
        if not result:
            print('Could not find a song arrangement for sentence: {}'.format(sentence))
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

    def search_playlists(self, s):
        results = []

        if self.playlists is None:
            self.playlists = self.api.get_all_user_playlist_contents()

        for playlist in self.playlists:
            tracks = playlist.get('tracks', [])
            for i, track in enumerate(tracks):
                track_info = track.get('track', {})
                for info in track_info.values():
                    if isinstance(info, str):
                        if alphanum(s) in alphanum(info):
                            track_place = '{}/{}'.format(i, len(tracks))
                            results.append((playlist['name'], track_place))
        return set(results)


@click.group()
@click.option('--dry-run', '-d', is_flag=True, help='Just print search results; don\'t actually create a playlist or add songs to it')
@click.option('--verbose', '-v', count=True, help='Print search information')
@click.pass_context
def main(ctx, dry_run, verbose):
    #   parser = argparse.ArgumentParser(description="Make a playlist and populate with songs. Store credentials in creds.json with format {'username': username, 'password': password}")
    #   args = parser.parse_args()
    ctx.obj['PlaylistMaker'] = PlaylistMaker(dry_run, verbose)


@main.command()
@click.option('--filename', '-f', help='Text file full of search terms. One song per line will be added to the playlist')
@click.option('--name', '-n', help='Name of the playlist. Defaults to the filename')
@click.option('--playlist-id', '-p', help='Use this playlist (by id) instead of creating a new one')
@click.option('--sentence', '-s', help='A sentence to write out using song names')
@click.pass_context
def create(ctx, filename, name, playlist_id, sentence):
    pm = ctx.obj['PlaylistMaker']
    playlist_name = name or filename

    if playlist_id is None:
        playlist_id = pm.make_playlist(playlist_name)

    if filename:
        with open(filename) as f:
            songartists = f.readlines()
        sids = pm.find_song_ids(songartists)
    elif sentence:
        sids = pm.sentence_to_song_ids(sentence)
    else:
        click.echo('Must provide source for playlist (filename or sentence)')
        return 1

    pm.populate_playlist(playlist_id, sids)
    pm.api.logout()


@main.command()
@click.argument('search-term')
@click.pass_context
def search(ctx, search_term):
    pm = ctx.obj['PlaylistMaker']
    results = pm.search_playlists(search_term)
    for result in results:
        click.echo(' '.join(result))


if __name__ == '__main__':
    main(obj={})
