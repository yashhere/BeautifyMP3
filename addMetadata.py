import musicbrainzngs as m
import sys, eyed3


def main():
    m.set_useragent(
        "RepairMusicMetadata", "0.1", "https://yashagarwal.me")

    music_path = "/home/yash/bf.mp3"
    file = eyed3.load(music_path)

    artist_name = file.tag.artist
    title = file.tag.title
    album = file.tag.album

    result = m.search_recordings(recording=title, country="IN", artist=artist_name, release=album)
    # print(result)

    for query in result['recording-list']:
        if(query['ext:score'] == "100"):
            # print(query['release-list'][0]['title'])
            # area = query['release-list'][0]['release-event-list'][0]['area']['name']
            # print(area)
            if(query['release-list'][0]['title'] == album):
                id = query['release-list'][0]['medium-list'][0]['track-list'][0]['id']
                print(id)
            else:
                print("Not Found")
    #         print(id)
    #         x = m.get_recording_by_id(id)
    #         print(x)
    #         break
    #     print(release)


if __name__ == "__main__":
    main()
