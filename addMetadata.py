#!/usr/bin/env python

DESC = """

______________________________________________________________
|                                                            |
|       Edit Metadata of MP3 files based on file name        |
|____________________________________________________________|
"""


import sys
from os import chdir, listdir, rename, walk, path, environ
from os.path import basename, dirname, realpath
import spotipy
import argparse
import configparser
import spotipy.oauth2 as oauth2
import re
from titlecase import titlecase
import requests
from bs4 import BeautifulSoup
import eyed3
import argparse


def setup_config():
    '''
        read api keys from config.ini file
    '''

    global CONFIG, GENIUS_KEY, SP_SECRET, SP_ID, config_path

    CONFIG = configparser.ConfigParser()
    config_path = realpath(__file__).replace(basename(__file__), '')
    config_path = config_path + 'config.ini'
    CONFIG.read(config_path)

    GENIUS_KEY = CONFIG['keys']['genius_key']
    SP_SECRET = CONFIG['keys']['spotify_client_secret']
    SP_ID = CONFIG['keys']['spotify_client_id']

    if GENIUS_KEY == '<insert genius key here>':
        print('Warning, you are missing Genius key. Add it using --config\n\n')

    if SP_SECRET == '<insert spotify client secret here>':
        print('Warning, you are missing Spotify Client Secret. Add it using --config\n\n')

    if SP_ID == '<insert spotify client id here>':
        print('Warning, you are missing Spotify Client ID. Add it using --config\n\n')


def add_config_keys():
    '''
        Adds configuration keys in the config.ini file
    '''

    GENIUS_KEY = CONFIG['keys']['genius_key']
    SP_SECRET = CONFIG['keys']['spotify_client_secret']
    SP_ID = CONFIG['keys']['spotify_client_id']

    if GENIUS_KEY == '<insert genius key here>':
        genius_key = input('Enter Genius Client Access token : ')
        CONFIG['keys']['genius_key'] = genius_key

    if SP_SECRET == '<insert spotify client secret here>':
        sp_secret = input('Enter Spotify Secret token : ')
        CONFIG['keys']['spotify_client_secret'] = sp_secret

    if SP_ID == '<insert spotify client id here>':
        sp_id = input('Enter Spotify Client ID : ')
        CONFIG['keys']['spotify_client_id'] = sp_id

    with open(config_path, 'w') as configfile:
        CONFIG.write(configfile)


def improve_song_names(songs):
    '''
        removes all unwanted words and numbers from file name so that the spotify search results can be improved

        removes all numbers from beginning, then strip all punctuation marks from the string, then remove words in word_filters, then remove unwanted space
    '''

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
    '''
        return search query for spotify api call
    '''

    return title + ' - ' + artist


def get_lyrics_genius(song_name):
    '''
        calls genius.com api for getting the url of the song lyrics page then scrapes that page to fetch the lyrics
    '''

    base_url = "https://api.genius.com"
    headers = {'Authorization': 'Bearer %s' % (GENIUS_KEY)}
    search_url = base_url + "/search"
    data = {'q': song_name}

    response = requests.get(search_url, data=data, headers=headers)
    json = response.json()

    try:
        song_info = json['response']['hits'][0]['result']['api_path']
    except KeyError:
        print("Could not find lyrics")
        return None
    except IndexError:
        print("Could not find lyrics")
        return None

    song_url = base_url + song_info
    response = requests.get(song_url, headers=headers)
    json = response.json()
    song_path = json['response']['song']['path']
    song_url = "http://genius.com" + song_path
    page = requests.get(song_url)
    html = BeautifulSoup(page.text, "html.parser")

    # remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('script')]

    lyrics = html.find("div", class_="lyrics").get_text()
    lyrics.replace('\n', ' ')
    return lyrics


def get_metadata_spotify(spotify, song_name):
    '''
        call spotify.com api to get the metadata required, as much as possible
    '''

    metadata = {}
    try:
        meta_tags = spotify.search(song_name, limit=1)['tracks']['items'][0]
    except IndexError:
        print("Could not find the song on Spotify")
        return []

    metadata['title'] = meta_tags['name']
    metadata['artist'] = meta_tags['artists'][0]['name']
    metadata['album'] = meta_tags['album']['name']
    metadata['album_artist'] = meta_tags['album']['artists'][0]['name']

    album_id = meta_tags['album']['id']
    album_meta_tags = spotify.album(album_id)

    metadata['release_date'] = album_meta_tags['release_date']
    try:
        metadata['total'] = album_meta_tags['tracks']['total']
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
    metadata['lyrics'] = get_lyrics_genius(
        get_song_name(metadata['title'], metadata['artist']))

    print(metadata)
    return metadata


def list_files():
    '''
        list all files in current directory with extension .mp3
    '''

    files = []
    return [f for f in listdir('.') if f.endswith('.mp3')]


def set_metadata(file_name, metadata):
    '''
        call eyed3 module to set mp3 song metadata as received from spotify
    '''

    audiofile = eyed3.load(file_name)
    tag = audiofile.tag

    try:
        tag.artist = metadata['artist']
        tag.album_artist = metadata['album_artist']
        tag.album = metadata['album']
        tag.title = metadata['title']
        tag.genre = metadata['genre']
        tag.track_num = metadata['track_num']
        tag.release_date = metadata['release_date']
        tag.disc_num = metadata['disc_num']
        # tag.lyrics.set(metadata['lyrics'])

        img = requests.get(
            metadata['albumart'], stream=True)
        img = img.raw

        albumart = img.read()
        tag.images.set(3, albumart, 'image/jpeg')

        tag.save(version=(2, 3, 0))

    except:
        return

    return


def main():
    '''
    Deals with arguements and calls other functions
    '''

    setup_config()

    parser = argparse.ArgumentParser(
        description="{}".format(DESC), formatter_class=argparse.RawDescriptionHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-d', '--dir', action="store", dest='repair_directory',
                       help='give path of music files\' directory', default='.')

    group.add_argument('-s', '--song', action='store', dest='song_name',
                       help='Only fix metadata of the file specified')

    parser.add_argument('-c', '--config', action='store_true', dest='config',
                        help="Add API Keys to config\n\n")

    parser.add_argument('-n', '--norename', action='store_true',
                        help='Does not rename files to song title\n\n')

    parser.add_argument('-f', '--format', action='store', dest='rename_format', help='''Specify the Name format used in renaming,
                        Valid Keywords are:
                        {title}{artist}{album}\n\n)''')

    args = parser.parse_args()

    repair_directory = args.repair_directory or '.'
    norename = args.norename or False
    format = args.rename_format or '{title}'
    config = args.config

    if config:
        add_config_keys()

    auth = oauth2.SpotifyClientCredentials(
        client_id=SP_ID, client_secret=SP_SECRET)
    token = auth.get_access_token()
    spotify = spotipy.Spotify(auth=token)

    files = list_files()
    improved_name = improve_song_names(files)

    metadata = get_metadata_spotify(
        spotify, "Martin Garrix and Bebe Rexha In The Name of Love")


if __name__ == "__main__":
    main()
