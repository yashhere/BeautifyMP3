import musicbrainzngs as m
import sys
from mutagen.id3 import ID3
from mutagen import File
import os
import mutagen
from os.path import basename
import spotipy

def improve_song_name(song):
    return song


def get_metadata(song):
    spotify = spotipy.Spotify()
    results = spotify.search(song_name, limit=1)

    results = results['tracks']['items'][0]  # Find top result
    album = results['album']['name']  # Parse json dictionary
    artist = results['album']['artists'][0]['name']
    song_title = results['name']
    album_art = results['album']['images'][0]['url']

    return artist, album, song_title, album_art

def add_metadata(files):
    # tags = File("/home/yash/Desktop/music-tagger/sample_songs/02. DJ Snake - Let Me Love You (Feat. Justin Bieber).mp3")
    # print(tags)
    for file in files:
        print(file)
        tags = File(file)
        song_name = basename(file[:-4])
        song_name = improve_song_name(song_name)

        title, artist, album, cover_art = get_metadata(song_name)


def list_files():
    files = []
    return [f for f in os.listdir('.') if f.endswith('.mp3')]


def main():
    m.set_useragent(
        "RepairMusicMetadata", "0.1", "https://yashagarwal.me")

    files = list_files()
    get_metadata("36. Galantis - No Money")
    # add_metadata(files)
    # result = m.search_releases("36. Galantis - No Money")
    # print(result)
    # for rel in result['release-list']:
    #     print("{}, by {}".format(rel['title'], rel["artist-credit-phrase"]))
    #     if 'date' in rel:
    #         print("Released {} ({})".format(rel['date'], rel['status']))
    #     print("MusicBrainz ID: {}".format(rel['id']))


if __name__ == "__main__":
    main()
