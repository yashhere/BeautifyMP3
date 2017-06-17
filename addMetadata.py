#!/usr/bin/env python

DESC = """

 ____                   _   _  __       __  __ ____ _____ 
| __ )  ___  __ _ _   _| |_(_)/ _|_   _|  \/  |  _ \___ / 
|  _ \ / _ \/ _` | | | | __| | |_| | | | |\/| | |_) ||_ \ 
| |_) |  __/ (_| | |_| | |_| |  _| |_| | |  | |  __/___) |
|____/ \___|\__,_|\__,_|\__|_|_|  \__, |_|  |_|_|  |____/ 
                                  |___/                   
                                  
______________________________________________________________
|                                                            |
|       Edit Metadata of MP3 files based on file name        |
|____________________________________________________________|
"""


import sys
import shutil
import os
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
        CONFIG['keys']['genius_key'] = str(genius_key)

    if SP_SECRET == '<insert spotify client secret here>':
        sp_secret = input('Enter Spotify Secret token : ')
        CONFIG['keys']['spotify_client_secret'] = str(sp_secret)

    if SP_ID == '<insert spotify client id here>':
        sp_id = input('Enter Spotify Client ID : ')
        CONFIG['keys']['spotify_client_id'] = str(sp_id)

    with open(config_path, 'w') as configfile:
        CONFIG.write(configfile)


def improve_song_name(song):
    '''
        removes all unwanted words and numbers from file name so that the spotify search results can be improved

        removes all numbers from beginning, then strip all punctuation marks from the string, then remove words in word_filters, then remove unwanted space
    '''

    char_filters = "()[]{}-:_/=!+\"\'"
    word_filters = ('lyrics', 'lyric', 'by', 'video', 'official', 'hd', 'dirty', 'with', 'lyrics', 'feat', 'original', 'mix',
                    'www', 'com', 'mp3', 'audio', 'remixed', 'remix', 'full', 'version', 'music', 'hq', 'uploaded', 'explicit')

    reg_exp = 's/^\d\d //'
    song = song.strip()
    song = song.lstrip("0123456789.- ")
    # re.sub(reg_exp, '', song)
    song = song[0:-4]
    song = ''.join(
        map(lambda c: " " if c in char_filters else c, song))

    song = re.sub('|'.join(re.escape(key) for key in word_filters),
                  "", song, flags=re.IGNORECASE)

    song = ' '.join(song.split()).strip()

    return song


def get_song_name(title, artist):
    '''
        return search query for spotify api call
    '''

    return title + ' - ' + artist


def get_lyrics_genius(song_name):
    '''
        calls genius.com api for getting the url of the song lyrics page then scrapes that page to fetch the lyrics
    '''

    GENIUS_KEY = "iazjdOEEunvS_XOXhmJTcUzOsvrEjaNIftCKj7PLrgZjjWXiFTeoNHVmwYRDMkx9"
    base_url = "https://api.genius.com"
    headers = {'Authorization': 'Bearer %s' % (GENIUS_KEY)}
    search_url = base_url + "/search"
    data = {'q': song_name}

    response = requests.get(search_url, data=data, headers=headers)
    json = response.json()

    try:
        song_info = json['response']['hits'][0]['result']['api_path']
    except KeyError:
        print("Could not find lyrics for " + song_name)
        return None
    except IndexError:
        print("Could not find lyrics for " + song_name)
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

    print("trying to find data on Spotify...")
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
        metadata['genre'] = titlecase(album_meta_tags['genres'][0])
    except IndexError:
        try:
            artist_id = meta_tags['artists'][0]['id']
            artist_meta_tags = spotify.artist(artist_id)
            metadata['genre'] = titlecase(artist_meta_tags['genres'][0])

        except IndexError:
            print("song genre could not be found.")
            pass

    metadata['track_num'] = meta_tags['track_number']
    metadata['disc_num'] = meta_tags['disc_number']

    metadata['albumart'] = meta_tags['album']['images'][0]['url']

    lyrics = get_lyrics_genius(get_song_name(
        metadata['title'], metadata['artist']))

    if lyrics is not None:
        metadata['lyrics'] = lyrics

    print()
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

    print("setting metadata for " + file_name)
    print()
    audiofile = eyed3.load(file_name)
    tag = audiofile.tag

    if 'genre' in metadata:
        tag.genre = metadata['genre']

    if 'lyrics' in metadata:
        tag.lyrics.set(metadata['lyrics'])

    img = requests.get(
        metadata['albumart'], stream=True)
    img = img.raw

    albumart = img.read()
    tag.images.set(3, albumart, 'image/jpeg')

    tag.save(version=(2, 3, 0))

    # if not norename:
    #     song_title = rename_format.format(
    #         title=metadata['title'] + ' -',
    #         artist=metadata['artist'] + ' -',
    #         album=metadata['album'] + ' -')

    # song_title = song_title[:-1] if song_title.endswith('-') else song_title
    # song_title = ' '.join(song_title.split()).strip()

    # print("renaming " + file_name + "to " + song_title)
    # new_path = path.dirname(file_name) + '{}.mp3'.format(song_title)
    # rename(file_name, new_path)

    print()
    return


def fix_music_file(spotify, file_name, norename, rename_format):
    print("------------------------------------------------------------------------")
    print()
    print()
    print("Currently processing " + file_name)
    metadata = get_metadata_spotify(spotify, improve_song_name(file_name))
    if not metadata:
        is_improvemet_needed = True
        return is_improvemet_needed
    else:
        set_metadata(file_name, metadata)
        is_improvemet_needed = False

        rename_file = rename_to_format(
            file_name, norename, rename_format, metadata)

        shutil.move(rename_file, 'Music')
        return is_improvemet_needed


def rename_to_format(file_name, norename, rename_format, metadata):
    if not norename:
        song_title = rename_format.format(
            title=metadata['title'] + ' -',
            artist=metadata['artist'] + ' -',
            album=metadata['album'] + ' -')

    song_title = song_title[:-1] if song_title.endswith('-') else song_title
    song_title = ' '.join(song_title.split()).strip()

    print("renaming " + file_name + "to " + song_title)
    new_path = path.dirname(file_name) + '{}.mp3'.format(song_title)
    rename(file_name, new_path)
    return new_path


def fix_music_files(spotify, files, norename, rename_format):
    need_to_improve = []
    for file_name in files:
        response = fix_music_file(spotify, file_name, norename, rename_format)

        if response is True:
            need_to_improve.append(file_name)

        ("------------------------------------------------------------------------")
        print()
        print()

    return need_to_improve


def main():
    '''
    Deals with arguements and calls other functions
    '''

    setup_config()

    parser = argparse.ArgumentParser(
        description="{}".format(DESC), formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('-d', '--dir', action="store", dest='repair_directory',
                        help='give path of music files\' directory', default=os.getcwd())

    parser.add_argument('-s', '--song', action='store', dest='song_name',
                        help='Only fix metadata of the file specified', default=None)

    parser.add_argument('-c', '--config', action='store_true', dest='config',
                        help="Add API Keys to config\n\n")

    parser.add_argument('-n', '--norename', action='store_true',
                        help='Does not rename files to song title\n\n')

    parser.add_argument('-f', '--format', action='store', dest='rename_format', help='''Specify the Name format used in renaming,
                        Valid Keywords are:
                        {title}{artist}{album}\n\n)''')

    args = parser.parse_args()

    repair_directory = args.repair_directory or '.'
    song_name = args.song_name or None
    norename = args.norename or False
    rename_format = args.rename_format or '{title}'
    config = args.config

    if config:
        add_config_keys()

    auth = oauth2.SpotifyClientCredentials(
        client_id="622a0e16a4914e3eadc2a37b4a134f1e", client_secret="6fe008a8b7754954a58a9849fa3172df")
    token = auth.get_access_token()
    spotify = spotipy.Spotify(auth=token)

    files = []

    if song_name is not None:
        need_to_improve = fix_music_file(
            spotify, song_name, norename, rename_format)
        if need_to_improve is True:
            print(song_name)

    elif repair_directory:
        chdir(repair_directory or '.')
        if not os.path.exists("Music"):
            os.makedirs("Music")
        files = list_files()
        need_to_improve = fix_music_files(
            spotify, files, norename, rename_format)
        print(need_to_improve)


if __name__ == "__main__":
    main()
