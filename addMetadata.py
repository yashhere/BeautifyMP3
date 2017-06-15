import sys
import os
import mutagen
from os.path import basename
import acoustid
import discogs_client as discogs
from string import digits


def improve_song_names(songs):
    text_file = open("blacklist.txt", "r")
    blacklistWords = text_file.read().splitlines()
    blacklistWords = [word.lower() for word in blacklistWords]

    for song in songs:
        searchText = song[0:-4]
        remove_digits = searchText.maketrans('', '', digits)
        searchText = searchText.translate(remove_digits)
        for word in song[0:-4].split(' '):
            if word.lower() in blacklistWords:
                searchText = searchText.replace(word, '')
        print(searchText)


def get_metadata_acoustid(song):
    API_KEY = 'GkQibmzT1u'
    try:
        results = acoustid.match(API_KEY, song)
    except acoustid.NoBackendError:
        print("chromaprint library/tool not found", file=sys.stderr)
        sys.exit(1)
    except acoustid.FingerprintGenerationError:
        print("fingerprint could not be calculated", file=sys.stderr)
        sys.exit(1)
    except acoustid.WebServiceError as exc:
        print("web service request failed:", exc.message, file=sys.stderr)
        sys.exit(1)

    # for result in results:
    #     print(result)
    first = True
    for score, rid, title, artist in results:
        if first:
            first = False
        else:
            return title, artist
            # print()
        # print('%s - %s' % (artist, title))
        # print('http://musicbrainz.org/recording/%s' % rid)
        # print('Score: %i%%' % (int(score * 100)))
        # break


def get_metadata_musicbrainz(song):
    return


def add_metadata(files):
    return


def list_files():
    files = []
    return [f for f in os.listdir('.') if f.endswith('.mp3')]


def get_metadata_discogs(song_name):
    d = discogs.Client('ExampleApplication/0.1',
                       user_token="mbNSnSrqdyJOKorCDBXjzzeYNhgulysWNJbwgBmk")
    results = d.search(song_name, type="release")
    # print(results.page(1))
    first_result = results.page(1)[0]

    # artist = first_result.artists[0].name
    title = first_result.title

    print(dir(first_result.artists[0]))
    print(title)
    print(first_result.artists[0].name)
    # print(title, artist)


def main():
    files = list_files()
    # title, artist = get_metadata_acoustid(
    # "21. Jonas Blue - By Your Side (Feat Raye).mp3")

    # title, artist =
    # get_metadata_discogs(
    #     "Jonas Blue - By Your Side (Feat Raye)")

    improve_song_names(files)
    # print(title, artist)


if __name__ == "__main__":
    main()
