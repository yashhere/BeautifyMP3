import musicbrainzngs as m
import sys


def show_release_details(rel):

    if rel['title'] != 'Half Girlfriend':
        return

    """Print some details about a release dictionary to stdout.
    """
    # "artist-credit-phrase" is a flat string of the credited artists
    # joined with " + " or whatever is given by the server.
    # You can also work with the "artist-credit" list manually.

    print("{}, by {}".format(rel['title'], rel["artist-credit-phrase"]))
    if 'date' in rel:
        print("Released {} ({})".format(rel['date'], rel['status']))
    print("MusicBrainz ID: {}".format(rel['id']))


def main():
    m.set_useragent(
        "RepairMusicMetadata", "0.1", "https://yashagarwal.me")
    # print(m.get_label_by_id("aab2e720-bdd2-4565-afc2-460743585f16"))

    result = m.search_releases(release='Half Girlfriend',
                               limit=5)

    p = m.search_releases("Raabta")
    print(p)
    # if not result['release-list']:
    #     sys.exit("no release found")
    # for (idx, release) in enumerate(result['release-list']):
    #     print("match #{}:".format(idx + 1))
    #     release_id = release['id']
    #     # type(release_id)
    #     print(release)
    # data = m.get_image_list(release_id)

    # print(data)
    # for image in data["images"]:
    #     if "Front" in image["types"] and image["approved"]:
    #         print("%s is an approved front image!" %
    #               image["thumbnails"]["large"])
    #         break
    #         print()


if __name__ == "__main__":
    main()
