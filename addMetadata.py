import sys
import os
from os.path import basename
import acoustid
import discogs_client as discogs
from string import digits
import musicbrainzngs as m
from mutagen.id3 import ID3, APIC, _util
from mutagen.mp3 import EasyMP3
from bs4 import BeautifulSoup


def improve_song_names(songs):
    text_file = open("blacklist.txt", "r")
    blacklistWords = text_file.read().splitlines()
    blacklistWords = [word.lower() for word in blacklistWords]

    improved_names = []
    for song in songs:
        searchText = song[0:-4]
        # remove_digits = searchText.maketrans('', '', digits)
        # searchText = searchText.translate(remove_digits)
        for word in song[0:-4].split(' '):
            if word.lower() in blacklistWords:
                searchText = searchText.replace(word, '')

        improved_names.append(searchText.strip())

    return improved_names


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
    except acoustid.FingerprintSubmissionError:
        print("Error")

    first = True
    for result in results:
        if first:
            first = False
        else:
            print(result)
            score, rid, title, artist = result[0], result[1], result[2], result[3]
            valid = True

    if first is True:
        print("No Data found for " + song + " .... Skipping it")
        valid = False
        score, rid, title, artist = None, None, None, None

    return valid, score, rid, title, artist


def get_metadata_musicbrainz(rid, artist, title):
    d = m.set_useragent(
        "MetadataRepair",
        "0.1",
        "https://github.com/yash2696/python-musicbrainzngs/",
    )

    result = m.search_recordings(
        artist=artist, recording=title, rid=rid, limit=5)

    print(result)


def add_metadata(file_name, rid, title, artist):

    return


def list_files():
    files = []
    return [f for f in os.listdir('.') if f.endswith('.mp3')]


def get_metadata_discogs(song_name):
    d = discogs.Client('ExampleApplication/0.1',
                       user_token="mbNSnSrqdyJOKorCDBXjzzeYNhgulysWNJbwgBmk")

    results = d.search(song_name, type="release")
    first_result = results.page(1)[0]

    # print(first_result)
    title = first_result.title

    # print(dir(first_result))
    print(title)
    print(first_result.artists[0].name)
    print(first_result.images[0])


def main():
    files = list_files()

    # title, artist =
    # get_metadata_discogs(
    #     "Jonas Blue - By Your Side (Feat Raye)")

    # get_metadata_discogs(
    #     "Maroon 5-Animals")
    # valid, score, rid, title, artist = get_metadata_acoustid(
    #     "18. Justin Timberlake - CAN'T STOP THE FEELING!.mp3")
    # print(valid)
    # print(score)
    # print(files)
    # for file_name in files:
    #     print("-------------" + file_name + "------------------")
    #     print()
    #     valid, score, rid, title, artist = get_metadata_acoustid(file_name)
    #     if valid == True:
    #         get_metadata_musicbrainz(rid, artist, title)
    #         add_metadata(file_name, rid, title, artist)
    #     print()
    #     break

    files = improve_song_names(files)
    # print(files)
    count = 0
    for file_name in files:
        print("-------------" + file_name + "------------------")
        print()
        get_metadata_discogs(file_name)
        count += 1
        if count > 5:
            break
        print()


if __name__ == "__main__":
    main()
