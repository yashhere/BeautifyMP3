import sys
import os
from os.path import basename
import acoustid
import discogs_client as discogs
import musicbrainzngs as m
import eyed3
from bs4 import BeautifulSoup
import requests
import json
import spotipy
import spotipy.oauth2 as oauth2
import re


def improve_song_names(songs):
    text_file = open("blacklist.txt", "r")
    blacklistWords = text_file.read().splitlines()
    blacklistWords = [word.lower() for word in blacklistWords]

    reg_exp = 's/^\d\d //'
    improved_names = []
    for song in songs:
        song = song.strip()
        song = song.lstrip("0123456789.- ")
        # re.sub(reg_exp, '', song)
        searchText = song[0:-4]
        for word in song[0:-4].split(' '):
            if word.lower() in blacklistWords:
                searchText = searchText.replace(word, '')

        improved_names.append(searchText.strip())

    return improved_names


def get_soup(url, headers):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_albumart_google(song_name):
    url = "https://www.google.co.in/search?q=" + \
        song_name.replace(" ", "_") + "&source=lnms&tbm=isch"

    HEADERS = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }

    soup = get_soup(url, HEADERS)
    ActualImages = []
    for a in soup.find_all("div", {"class": "rg_meta"}):
        link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
        return link
        print(link)
        ActualImages.append((link, Type))

    return ActualImages


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
    scoreMax = 0

    for result in results:
        if first:
            first = False
        else:
            # print(result)
            if(result[0] > scoreMax):
                scoreMax = result[0]
            else:
                pass
            score, rid, title, artist = result[0], result[1], result[2], result[3]
            valid = True
            albumart = get_albumart_google(title + " - " + artist)
            break

    if first is True:
        print("No Data found for " + song + " .... Skipping it")
        score = rid = title = artist = albumart = None
        valid = False

    return valid, score, rid, title, artist, albumart


def get_metadata_musicbrainz(rid, artist, title):
    d = m.set_useragent(
        "MetadataRepair",
        "0.1",
        "https://github.com/yash2696/python-musicbrainzngs/",
    )

    result = m.search_recordings(
        artist=artist, recording=title, rid=rid, limit=5)

    print(result)


def list_files():
    files = []
    return [f for f in os.listdir('.') if f.endswith('.mp3')]


def get_metadata_discogs(song_name):
    d = discogs.Client('ExampleApplication/0.1',
                       user_token="mbNSnSrqdyJOKorCDBXjzzeYNhgulysWNJbwgBmk")

    results = d.search(song_name, type="release")
    first_result = results.page(1)[0]

    title = first_result.title

    print(title)
    print(first_result.artists[0].name)
    print(first_result.images[0])


def add_metadata(file_name, album_art):
    """
    Add album_art in .mp3's tags
    """

    img = requests.get(
        "https://i.ytimg.com/vi/7S0MWoXYH5k/maxresdefault.jpg", stream=True)
    img = img.raw

    audiofile = eyed3.load(file_name)
    tag = audiofile.tag

    tag.artist = "Alka Yagnik"
    tag.album = "Lajja"
    tag.title = "Badi Mushkil Baba Badi Mushkil"
    tag.images.set(3, img.read(), "image/jpeg", u"Google image")
    tag.lyrics.set(u""" """)

    # write it back
    audiofile.tag.save()


# def get_metadata_spotify(song):
#     spotify.search(song, limit=1)['tracks']['items'][0]
#     return


def main():
    auth = oauth2.SpotifyClientCredentials(
        client_id='622a0e16a4914e3eadc2a37b4a134f1e',
        client_secret='6fe008a8b7754954a58a9849fa3172df')
    token = auth.get_access_token()
    spotify = spotipy.Spotify(auth=token)

    files = list_files()
    improved_name = improve_song_names(files)

    # get_metadata_spotify(files[1])

    # valid, score, rid, title, artist, albumart = get_metadata_acoustid(
    #     "35. Mike Posner - I Took a Pill in Ibiza (SeeB Remix).mp3")

    # print(valid, score, rid, title, artist, albumart)
    # add_album_art(
    #     "Badi.mp3", "")
    # for file_name in files:
    #     print("-------------" + file_name + "------------------")
    #     print()
    #     valid, score, rid, title, artist = get_metadata_acoustid(file_name)
    #     if valid == True:
    #         get_metadata_musicbrainz(rid, artist, title)
    #         add_metadata(file_name, rid, title, artist)
    #     print()
    #     break

    # files = improve_song_names(files)
    # print(files)
    # count = 0
    # for file_name in files:
    #     print("-------------" + file_name + "------------------")
    #     print()
    #     get_metadata_discogs(file_name)
    #     count += 1
    #     if count > 5:
    #         break
    #     print()

    # get_albumart_google(
    #     "Mike Posner - I Took a Pill in Ibiza (acoustic)")


if __name__ == "__main__":
    main()
