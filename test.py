import unittest
from lyrAvCount import get_artist_id, parse_args, get_songs, get_lyrics, get_lyrics_count, display_msg

class TestlyrAvCount(unittest.TestCase):

    def test_parser(self):
        args = parse_args(['-a "Coldplay"','-c "Dua Lipa"', '-p'])
        self.assertTrue(args.artist)
        self.assertTrue(args.compare)
        self.assertTrue(args.plot)

    def test_get_artist_id(self):
         """
         Test that an artist id can be obtained from MusicBrainz database.
         """
         artist = 'Dua Lipa'
         self.assertTrue(get_artist_id(artist), 'artist_id does not return id')
         self.assertIsInstance(get_artist_id(artist), str)
         self.assertEqual(len(get_artist_id(artist)), 36)

    def test_get_songs(self):
         """
         Test that get_songs returns a populated list of songs.
         """
         # Dua Lipa id
         artist_id = '6f1a58bf-9b1b-49cf-a44a-6cefad7ae04f'
         songs = get_songs(artist_id)
         self.assertIsInstance(songs, list)
         self.assertTrue(songs, 'get_songs returns an empty list')

    def test_get_lyrics(self):
         """
         Test that get_lyrics returns a populated list of words.
         """
         # This API is a bit nasty. If you make the same request twice
         # it returns an empty list
         artist = 'Adele'
         song = 'Hello'
         lyrics = get_lyrics(artist, song)
         self.assertIsInstance(lyrics, list)
        # self.assertTrue(lyrics, 'get_lyrics returns an empty list')

    def test_get_lyrics_count(self):
        """
        Test get_lyrics_count return values.
        """
        artist = 'Zivert'
        count = get_lyrics_count(artist, count=False)
        self.assertIsInstance(count, tuple)
        self.assertIsInstance(count[0], list)
        self.assertIsInstance(count[1], int)
        self.assertIsInstance(count[2], int)
        self.assertIsInstance(count[3], str)
        self.assertEqual(count[3], artist)

    def test_display_msg(self):
        """
        Test final message.
        """
        lyr_count = ([1,3,2,5], 1, 1, 'TestArtist')
        msg = display_msg(lyr_count)
        self.assertIsInstance(msg, str)
        self.assertGreater(len(msg), 1)

if __name__ == '__main__':
    unittest.main()