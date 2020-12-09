import requests
import re
import sys
import time
import argparse
import statistics
import matplotlib.pyplot as plt


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--artist", help="artist name, i.e. 'OneRepublic', 'Dua Lipa'", required=True, metavar='')
    parser.add_argument("-c", "--compare", help="compare with another artist, i.e. 'Imagine Dragons', 'Ava Max' (argument can be used multiple times)",
                        action='append', required=False, metavar='')
    parser.add_argument("-p", "--plot", help="plot lyrics count statistics",
                        required=False, action='store_true')
    return parser.parse_args(args)


def get_artist_id(artist):
    url = f'https://musicbrainz.org/ws/2/artist/?query={artist}'
    response = requests.request(
        "GET", url, headers={'Accept': 'application/json'})
    response = response.json()
    for key in response['artists']:
        if key['name'] == artist:
            artist_id = key['id']
            # If there are two artists with exactly the same name then there will be a problem
            # since the last one in the list who meets the condition will be selected.
            # This needs to be considered in a real application
    try:
        artist_id
    except NameError:
        sys.exit("Artist's name not found.")
    else:
        return artist_id


def get_songs(artist_id):
    songs_list = []
    duplicate_songs = []
    limit = 100
    offset = 0
    url = f'https://musicbrainz.org/ws/2/recording?artist={artist_id}&limit={limit}&offset={offset}'
    response = requests.request(
        "GET", url, headers={'Accept': 'application/json'})
    response = response.json()
    recording_count = response['recording-count']

    if recording_count > limit:
        while recording_count > (limit+offset):
            url = f'https://musicbrainz.org/ws/2/recording?artist={artist_id}&limit={limit}&offset={offset}'
            response = requests.request(
                "GET", url, headers={'Accept': 'application/json'})

            # If the response is not 200, try to connect again 3 times every 10 seconds
            # or exit the program with a message
            if response.status_code != 200:
                timeout = time.time() + 30
                print('Trying to reconnect to the recordings API, response:',
                      response.status_code)
                while time.time() < timeout and response.status_code != 200:
                    time.sleep(10)
                    response = requests.request(
                        "GET", url, headers={'Accept': 'application/json'})
                if response.status_code != 200:
                    sys.exit('Could not connect to the API')
                else:
                    print('Connection established')

            response = response.json()
            for key in response['recordings']:
                songs_list.append(key['title'])
            offset += limit
    else:
        for key in response['recordings']:
            songs_list.append(key['title'])

    # Remove initial repetitions
    songs_list = list(set(songs_list))
    # Remove description in brackets and forward slashes from recordings,
    # i.e. 'Songname / Name (Remix)' becomes 'Songname Name'

    for i in range(len(songs_list)):
        songs_list[i] = re.sub("[\(\[].*?[\)\]]", "", songs_list[i])
        songs_list[i] = re.sub(r"(\s+$)|(/)", "", songs_list[i])

    # Remove repetitions after re.sub parsing
    songs_list = list(set(songs_list))
    # Filter out '' elements if present
    songs_list = list(filter(lambda x: x != '', songs_list))

    # Find duplicate songs, i.e. 'Songname '96', 'Songname '98' and 'Songname'
    # Note: this removes subsequent version, i.e. Fly, Fly 2, Fly 3, etc.
    for i in range(len(songs_list)):
        for j in range(len(songs_list)):
            if songs_list[j].find(songs_list[i]) != -1 and songs_list[i] != songs_list[j]:
                duplicate_songs.append(songs_list[j])

    # Remove identical entries from the duplicate list.
    # This does not affect the next step but makes
    # the list easier to investigate
    duplicate_songs = list(set(duplicate_songs))

    # Remove duplicate songs from the songs list
    unique_songs = [song for song in songs_list if song not in duplicate_songs]
    unique_songs = list(set(unique_songs))
    unique_songs.sort()
    return unique_songs


def get_lyrics(artist, title):
    url = f'https://api.lyrics.ovh/v1/{artist}/{title}'
    response = requests.request("GET", url)

    # If the response is not 200, try to connect again 3 times every 10 seconds
    # or exit the program with error
    timeout = time.time() + 30
    if response.status_code != 200:
        print('Trying to connect to the lyrics API, response:', response.status_code)
        while time.time() < timeout and response.status_code != 200:
            print(artist, title)
            time.sleep(10)
            response = requests.request("GET", url)
        if response.status_code != 200:
            sys.exit('Could not connect to the API')
    response = response.json()
    lyrics = [word for word in response['lyrics'].strip('\n').split()]
    return lyrics


def get_lyrics_count(artist, count=True):
    songs_list = get_songs(get_artist_id(artist))
    lyrics_count_list = []
    number_of_songs = len(songs_list)
    songs_not_found = 0
    for i in range(len(songs_list)):
        lyrics_count = len(get_lyrics(artist, songs_list[i]))
        if count:
            sys.stdout.write(f'\rCounting {round(((i+1)/len(songs_list)*100))} % complete ({artist})')
            sys.stdout.flush()
        if lyrics_count != 0:
            lyrics_count_list.append(lyrics_count)
        else:
            songs_not_found += 1
    print('\n')
    return (lyrics_count_list, number_of_songs, songs_not_found, artist)


def get_plots(lyrics_stat):
    lyrics_list = lyrics_stat[0]
    artist = lyrics_stat[3]
    if len(lyrics_list) > 0:
        lyrics_average = round(statistics.mean(lyrics_list))
        min_words = min(lyrics_list)
        max_words = max(lyrics_list)
    else:
        lyrics_average = 0
        min_words = 0
        max_words = 0
    if len(lyrics_list) > 1:
        lyrics_stdev = round(statistics.stdev(lyrics_list))
    else:
        lyrics_stdev = False

    fig = plt.figure(figsize=(10, 5))
    x = [x+1 for x in range(len(lyrics_list))]
    plt.bar(x, lyrics_list, color='maroon', width=0.4)
    plt.axhline(y=lyrics_average, color='r', linestyle='-',
                label=f'Average {lyrics_average} words')
    if lyrics_stdev:
        plt.axhline(y=lyrics_stdev, color='g', linestyle='-',
                    label=f'stdev {lyrics_stdev}')
    plt.plot([], [], ' ', label=f'Minimum {min_words} words')
    plt.plot([], [], ' ', label=f'Maximum {max_words} words')
    plt.xlabel('Song')
    plt.ylabel('Word count')
    plt.title(f'Word count per song for {artist}')
    plt.legend(loc=1)


def display_msg(lyr_stats):
    if len(lyr_stats[0]) > 0:
        lyrics_average = round(statistics.mean(lyr_stats[0]))
    else:
        lyrics_average = 0
    songs_found = lyr_stats[1] - lyr_stats[2]
    msg = f'Lyrics average for {lyr_stats[3]} is {lyrics_average} '
    msg += f'({songs_found} out of {lyr_stats[1]} songs found in the database)'
    return msg


def main():
    args = parse_args(sys.argv[1:])
    artists_list = []
    artist = args.artist
    lyr_stats = get_lyrics_count(artist)
    artists_list.append(lyr_stats)
    if args.compare:
        artists = args.compare
        for artist in artists:
            lyr_stats = get_lyrics_count(artist)
            artists_list.append(lyr_stats)
    for artist in artists_list:
        print(display_msg(artist))
    if args.plot:
        for artist in artists_list:
            get_plots(artist)
        plt.show()


if __name__ == "__main__":
    main()
