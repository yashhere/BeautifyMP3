import sys
import os
from os.path import basename
import spotipy
import spotipy.oauth2 as oauth2
import re
from titlecase import titlecase
import requests
from bs4 import BeautifulSoup


def improve_song_names(songs):
    char_filters = "()[]{}-:_/=+\"\'"
    word_filters = ('lyrics', 'lyric', 'by', 'video', 'official', 'hd', 'dirty', 'with', 'lyrics', 'feat', 'original', 'mix',
                    'www', 'com', 'mp3', 'audio', 'remixed', 'remix', 'full', 'version', 'music', 'hq', 'uploaded', 'explicit')

    reg_exp = 's/^\d\d //'
    improved_names = []
    for song in songs:
        song = song.strip()
        song = song.lstrip("0123456789.- ")
        # re.sub(reg_exp, '', song)
        song = song[0:-4]
        song = ''.join(
            map(lambda c: " " if c in char_filters else c, song))

        song = re.sub('|'.join(re.escape(key) for key in word_filters),
                      "", song, flags=re.IGNORECASE)

        song = ' '.join(song.split())
        improved_names.append(song.strip())

    return improved_names


def get_song_name(title, artist):
    return title + ' - ' + artist


def get_metadata_spotify(spotify, song_name):
    metadata = {}
    meta_tags = spotify.search(song_name, limit=1)['tracks']['items'][0]

    metadata['title'] = meta_tags['name']
    metadata['artist'] = meta_tags['artists'][0]['name']
    metadata['album'] = meta_tags['album']['name']
    metadata['album_artist'] = meta_tags['album']['artists'][0]['name']

    album_id = meta_tags['album']['id']
    album_meta_tags = spotify.album(album_id)

    metadata['release-date'] = album_meta_tags['release_date']
    try:
        metadata['genre'] = titlecase(album_meta_tags['genres'][0])
    except IndexError:
        try:
            artist_id = meta_tags['artists'][0]['id']
            artist_meta_tags = spotify.artist(artist_id)
            metadata['genre'] = titlecase(artist_meta_tags['genres'][0])

        except IndexError:
            pass

    metadata['track_num'] = meta_tags['track_number']
    metadata['disc_num'] = meta_tags['disc_number']

    metadata['albumart'] = meta_tags['album']['images'][0]['url']
    # metadata['lyrics'] = get_lyrics_genius(
    #     get_song_name(metadata['title'], metadata['artist']))

    return metadata


def list_files():
    files = []
    return [f for f in os.listdir('.') if f.endswith('.mp3')]


def main():
    auth = oauth2.SpotifyClientCredentials(
        client_id='622a0e16a4914e3eadc2a37b4a134f1e',
        client_secret='6fe008a8b7754954a58a9849fa3172df')
    token = auth.get_access_token()
    spotify = spotipy.Spotify(auth=token)

    files = list_files()
    improved_name = improve_song_names(files)

    # print(improved_name[19])
    # print(files[16])
    metadata = get_metadata_spotify(
        spotify, improved_name[19])


if __name__ == "__main__":
    main()
