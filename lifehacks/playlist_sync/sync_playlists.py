#!/usr/bin/env python3

from functools import lru_cache
import json
import re

#import click
from gmusicapi import Mobileclient
import requests
import spotipy
from spotipy import oauth2 as spoauth2


def alphanum(s):
    return re.sub(r'[^a-z0-9]+', '', str(s).lower())


def word_soup(s):
    return sorted(w for w in s.split() if not w.lower() in ('a', 'an', 'the', 'ft', 'feat', 'featuring'))


@lru_cache(maxsize=256)
def edit_distance(a, b):
    if not a or not b:
        return len(a) or len(b)

    if a[0] == b[0]:
        return edit_distance(a[1:], b[1:])
    else:
        return min(edit_distance(a[1:], b) + 1, edit_distance(a[1:], b[1:]) + 1, edit_distance(a, b[1:]) + 1)


def unique_in(set_a, set_b):
    return (s for s in list(set_a) if not any(map(lambda x: x == s, set_b)))


# TODO: dataclass
class Song:
    def __init__(self, title, artist):
        # Strip parentheticals and anything in brackets; this can lose us some
        # real parts of song names e.g. Absolutely (Story of a Girl), but is
        # more likely to lose extraneous info e.g. (ft. Ludacris) or
        # (Remastered). Also dump anything after a hyphen for the same reason.
        self.title = re.sub(r'\[[^)]*\]', '',  re.sub(r'\([^)]*\)', '', title)).split('-')[0].strip()
        self.artist = artist

    def __repr__(self):
        return f'{self.title} - {self.artist}'

    def __hash__(self):
        return hash(alphanum(str(self)))

    def __eq__(self, other):
        st = alphanum(self.title)
        sa = alphanum(self.artist)

        ot = alphanum(other.title)
        oa = alphanum(other.artist)

        # Account for only one artist out of a set being credited and
        # misspellings (e.g. Kesha/Ke$ha). Since both the title and artist have
        # to match, it's probably fine to pick an absolute threshold and not a
        # relative one, but...
        edpt = edit_distance(st, ot)/max(len(st), len(ot))
        edpa = edit_distance(sa, oa)/max(len(sa), len(oa))

        # Maybe use word soup to account for artists being listed in different orders

        return (st == ot or st in ot or ot in st or edpt < 0.25) and \
                (sa == oa or sa in oa or oa in sa or edpa < 0.25)


class PlaylistSyncer:
    def __init__(self):
        self.gsongs = set()
        self.spsongs = set()

        with open('creds.json') as f:
            self.creds = json.loads(f.read())

        self.gapi = Mobileclient()
        self.glogged_in = self.gapi.login(self.creds['gmusic_username'], self.creds['gmusic_password'], Mobileclient.FROM_MAC_ADDRESS)
        self.spcc = spoauth2.SpotifyClientCredentials(client_id=self.creds['spotify_client_id'], client_secret=self.creds['spotify_client_secret'])
        self.spapi = spotipy.Spotify(auth=self.spcc.get_access_token())

        self.force_load_gmusic_playlist()
        self.load_spotify_playlist()


    def force_load_gmusic_playlist(self):
        url = 'https://play.google.com/music/services/loaduserplaylist'
        params = {'format': 'jsarray',
                  'xt': self.creds['gmusic_xt']}

        # TODO: See if there's some way to create this cookie rather than manually setting it
        # Will it expire?
        # A: yes, but only every few months
        # xt, on the other hand
        response = requests.post(url, params=params, data='[[],["{}"]]'.format(self.creds['gmusic_playlist_id']), headers={'cookie': self.creds['gmusic_cookie']})
        tracks = response.json()[1][0]

        self.gsongs = set()
        for track in tracks:
            self.gsongs.add(Song(track[1], track[3]))

    def load_spotify_playlist(self):
        pl = self.spapi.user_playlist(self.creds['spotify_user_id'], self.creds['spotify_playlist_id'])
        tracks = pl['tracks']
        for track in tracks['items']:
            t = track['track']
            self.spsongs.add(Song(t['name'], ' & '.join(a['name'] for a in t['artists'])))

        while tracks['next']:
            tracks = self.spapi.next(tracks)
            for track in tracks['items']:
                t = track['track']
                self.spsongs.add(Song(t['name'], ' & '.join(a['name'] for a in t['artists'])))

    def symmetric_song_difference(self):
        diff = set()
        # lmao can't use anything that uses hashes
        diff.update(unique_in(self.gsongs, self.spsongs))
        diff.update(unique_in(self.spsongs, self.gsongs))
        return diff

    def update_gmusic(self):
        to_add = unique_in(self.spsongs, self.gsongs)
        for song in to_add:
            results = self.gapi.search(str(song))
            hits = results.get('song_hits')
            if hits:
                pass

            print(results)
            # search for song
            # add song to playlist


        return to_add

    def update_spmusic(self):
        to_add = unique_in(self.gsongs, self.spsongs)
        return to_add

    def sync(self):
        self.update_gmusic()
        self.update_spmusic()
