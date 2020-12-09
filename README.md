# lyrAvCount CLI program

A simple CLI program which, when given the name of an artist, will produce the average
number of words in their songs. The program can list multiple artists at once via `-c` arguments (these can be provided multiple times). The final output shows how many songs the artist has and how many of the lyrics for these songs were successfully found in the database.

The tool plots the data with the `-p` argument. Figures show the word count per song (song names are not displayed), the average, minimum and maximum words in the songs list and the standard deviation if there is more than one song in the list. 

### NOTES:
- Making the same lyrics request multiple times in a short period gives an empty list for the lyrics.
- The program does not show the progress while browsing MusicBrainz database. However, it notifies the user if it encounters a problem while doing so. MusicBrainz API rejects the requests after 13-14 attempts in a short period of time. If that happens the program waits for a few seconds and tries to resume the search, i.e. `python lyrAvCount.py -a 'Coldplay'` should illustrate that. If it does not succeed then it exits with a message.
- Same approach is used for the lyrics API as it returns error 404 if the request has a song title whith wierd symbols which were missed by the parser.
- There is a progress update message `Counting X % complete (Artist)` while using the lyrics API.

## Requirements
Python3.6 or greater (use of f-strings). Modules used:
- `requests`
- `re`
- `sys`
- `time`
- `argparse`
- `statistics`
- `matplotlib.pyplot`
- `unittest`

Using `pip install requests, matplotlib` should be enough to get you going. However, there is also a `requirements.txt` file which can be used with `pip install -r requirements.txt`.  

## Usage
usage: `python3 lyrAvCount.py [-h] -a [-c] [-p]`

optional arguments:
-  -h, --help       show this help message and exit
-  -a , --artist    artist name, i.e. 'OneRepublic', 'Dua Lipa'
-  -c , --compare   compare with another artist, i.e. 'Imagine Dragons', 'Ava Max' (argument can be used multiple times)
-  -p, --plot       plot lyrics count statistics

Example usage: `python3 .\lyrAvCount.py -a 'Dua Lipa' -c 'Imagine Dragons' -c 'OneRepublic' -p`
This should display the average count for the three artists and plot the data on three graphs. Only the `-a` argument is mandatory, hence `python3 .\lyrAvCount.py -a 'Coldplay'` will also work.

## Unit test cases

The unit test cases are in the `test.py` file. They check the expected output of the functions.

Running: `python3 test.py` should complete 6 tests in about 20 seconds.

## Next Development Steps

- Get familiar with MusicBrainz` API in more details and check if it is possible to obtain songs (recordings) in a better way that parsing duplicate names.
- Research lyrics API since it does not return the lyrics of all songs (probably related to parsing the titles).
- Expand plotting functionality for better visualisation.
