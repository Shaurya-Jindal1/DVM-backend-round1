from unittest.mock import patch, Mock

from django.test import TestCase
from django.urls import reverse


def make_response(data):
    # fake version of the response object that requests.get returns
    response = Mock()
    response.json.return_value = data
    return response


IMAGES = [
    {'#text': 'small.png', 'size': 'small'},
    {'#text': 'medium.png', 'size': 'medium'},
    {'#text': 'large.png', 'size': 'large'},
    {'#text': 'extralarge.png', 'size': 'extralarge'},
]

TOP_ARTISTS = {
    'topartists': {
        'artist': [
            {'name': 'Arijit Singh', 'listeners': '1386563', 'url': 'https://www.last.fm/music/Arijit+Singh', 'image': IMAGES},
            {'name': 'The Weeknd', 'listeners': '6214539', 'url': 'https://www.last.fm/music/The+Weeknd', 'image': IMAGES},
        ],
        '@attr': {'country': 'India', 'page': '1', 'perPage': '20', 'totalPages': '50', 'total': '1000'},
    }
}

TOP_TRACKS = {
    'tracks': {
        'track': [
            {
                'name': 'Blinding Lights',
                'listeners': '3000000',
                'url': 'https://www.last.fm/music/The+Weeknd/_/Blinding+Lights',
                'artist': {'name': 'The Weeknd', 'url': 'https://www.last.fm/music/The+Weeknd'},
                'image': IMAGES,
            },
        ],
        '@attr': {'country': 'India', 'page': '1', 'perPage': '20', 'totalPages': '10', 'total': '200'},
    }
}

ARTIST_SEARCH = {
    'results': {
        'opensearch:totalResults': '71388',
        'artistmatches': {
            'artist': [
                {'name': 'Cher', 'listeners': '1392412', 'url': 'https://www.last.fm/music/Cher', 'image': IMAGES},
            ]
        },
    }
}

ALBUM_SEARCH = {
    'results': {
        'opensearch:totalResults': '5',
        'albummatches': {
            'album': [
                {'name': 'Believe', 'artist': 'Cher', 'url': 'https://www.last.fm/music/Cher/Believe', 'image': IMAGES},
            ]
        },
    }
}

ARTIST_INFO = {
    'artist': {
        'name': 'Radiohead',
        'url': 'https://www.last.fm/music/Radiohead',
        'image': IMAGES,
        'stats': {'listeners': '5000000', 'playcount': '900000000'},
        'similar': {'artist': [{'name': 'Thom Yorke', 'url': 'https://www.last.fm/music/Thom+Yorke'}]},
        'tags': {'tag': [{'name': 'alternative'}, {'name': 'rock'}]},
        'bio': {'summary': 'Radiohead are an English rock band. <a href="https://www.last.fm/music/Radiohead">Read more on Last.fm</a>'},
    }
}

ARTIST_TOP_TRACKS = {
    'toptracks': {
        'track': [
            {'name': 'Creep', 'playcount': '12345', 'url': 'https://www.last.fm/music/Radiohead/_/Creep'},
        ]
    }
}

USER_INFO = {
    'user': {
        'name': 'rj',
        'realname': 'Richard Jones',
        'url': 'https://www.last.fm/user/RJ',
        'image': IMAGES,
        'country': 'United Kingdom',
        'playcount': '150316',
        'artist_count': '11275',
        'registered': {'unixtime': '1037793040', '#text': 1037793040},
    }
}

USER_TOP_ARTISTS = {
    'topartists': {'artist': [{'name': 'Four Tet', 'playcount': '500', 'image': IMAGES}]}
}

USER_TOP_TRACKS = {
    'toptracks': {'track': [{'name': 'Angel Echoes', 'playcount': '50', 'artist': {'name': 'Four Tet'}}]}
}

USER_RECENT_TRACKS = {
    'recenttracks': {
        'track': [
            {
                'name': 'Weird Fishes/Arpeggi',
                'artist': {'#text': 'Radiohead'},
                'album': {'#text': 'In Rainbows'},
                'image': IMAGES,
                '@attr': {'nowplaying': 'true'},
            },
            {
                'name': 'Angel Echoes',
                'artist': {'#text': 'Four Tet'},
                'album': {'#text': 'There Is Love in You'},
                'image': IMAGES,
                'date': {'uts': '1716200000', '#text': '20 May 2024, 10:13'},
            },
        ]
    }
}

WEEKLY_ARTISTS = {
    'weeklyartistchart': {
        'artist': [{'name': 'Radiohead', 'playcount': '42'}],
        '@attr': {'user': 'rj', 'from': '1716120000', 'to': '1716724800'},
    }
}

WEEKLY_TRACKS = {
    'weeklytrackchart': {
        'track': [{'name': 'Creep', 'playcount': '7', 'artist': {'#text': 'Radiohead'}}],
        '@attr': {'user': 'rj', 'from': '1716120000', 'to': '1716724800'},
    }
}

ERROR = {'error': 6, 'message': 'User not found'}


def fake_api(responses):
    """returns a function that picks the right fake response based on the method param"""
    def fake_get(url, params=None):
        return make_response(responses[params['method']])
    return fake_get


class HomePageTests(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('lastfm:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Top charts by country')


class ChartsTests(TestCase):
    def test_no_country(self):
        response = self.client.get(reverse('lastfm:charts'))
        self.assertEqual(response.status_code, 200)

    @patch('lastfm.views.requests.get')
    def test_top_artists(self, mock_get):
        mock_get.return_value = make_response(TOP_ARTISTS)
        response = self.client.get(reverse('lastfm:charts'), {'country': 'India'})
        self.assertContains(response, 'Arijit Singh')
        self.assertContains(response, 'The Weeknd')
        self.assertContains(response, 'Page 1 of 50')
        # check the right parameters were sent to the api
        params = mock_get.call_args[1]['params']
        self.assertEqual(params['method'], 'geo.gettopartists')
        self.assertEqual(params['country'], 'India')
        self.assertEqual(params['format'], 'json')

    @patch('lastfm.views.requests.get')
    def test_top_tracks(self, mock_get):
        mock_get.return_value = make_response(TOP_TRACKS)
        response = self.client.get(reverse('lastfm:charts'), {'country': 'India', 'type': 'tracks'})
        self.assertContains(response, 'Blinding Lights')
        self.assertEqual(mock_get.call_args[1]['params']['method'], 'geo.gettoptracks')

    @patch('lastfm.views.requests.get')
    def test_invalid_country(self, mock_get):
        mock_get.return_value = make_response({'error': 6, 'message': 'country param invalid'})
        response = self.client.get(reverse('lastfm:charts'), {'country': 'Atlantis'})
        self.assertContains(response, 'country param invalid')


class SearchTests(TestCase):
    @patch('lastfm.views.requests.get')
    def test_search_artist(self, mock_get):
        mock_get.return_value = make_response(ARTIST_SEARCH)
        response = self.client.get(reverse('lastfm:search'), {'q': 'cher'})
        self.assertContains(response, 'Cher')
        self.assertContains(response, '71,388 results')

    @patch('lastfm.views.requests.get')
    def test_search_album(self, mock_get):
        mock_get.return_value = make_response(ALBUM_SEARCH)
        response = self.client.get(reverse('lastfm:search'), {'q': 'believe', 'type': 'album'})
        self.assertContains(response, 'Believe')
        self.assertEqual(mock_get.call_args[1]['params']['method'], 'album.search')

    @patch('lastfm.views.requests.get')
    def test_empty_search_doesnt_call_api(self, mock_get):
        response = self.client.get(reverse('lastfm:search'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_get.called)

    @patch('lastfm.views.requests.get')
    def test_connection_error(self, mock_get):
        mock_get.side_effect = Exception('no internet')
        response = self.client.get(reverse('lastfm:search'), {'q': 'cher'})
        self.assertContains(response, 'Could not connect to Last.fm')


class ArtistPageTests(TestCase):
    @patch('lastfm.views.requests.get')
    def test_artist_page(self, mock_get):
        mock_get.side_effect = fake_api({
            'artist.getinfo': ARTIST_INFO,
            'artist.gettoptracks': ARTIST_TOP_TRACKS,
        })
        response = self.client.get(reverse('lastfm:artist', args=['Radiohead']))
        self.assertContains(response, 'Radiohead are an English rock band.')
        self.assertContains(response, 'Creep')
        self.assertContains(response, 'Thom Yorke')
        self.assertContains(response, 'alternative')


class UserProfileTests(TestCase):
    @patch('lastfm.views.requests.get')
    def test_user_profile(self, mock_get):
        mock_get.side_effect = fake_api({
            'user.getinfo': USER_INFO,
            'user.gettopartists': USER_TOP_ARTISTS,
            'user.gettoptracks': USER_TOP_TRACKS,
            'user.getrecenttracks': USER_RECENT_TRACKS,
        })
        response = self.client.get(reverse('lastfm:user_profile', args=['rj']))
        self.assertContains(response, 'Richard Jones')
        self.assertContains(response, 'Four Tet')
        self.assertContains(response, 'Angel Echoes')
        self.assertContains(response, 'Now playing')

    @patch('lastfm.views.requests.get')
    def test_user_not_found(self, mock_get):
        mock_get.return_value = make_response(ERROR)
        response = self.client.get(reverse('lastfm:user_profile', args=['nobodyhere12345']))
        self.assertContains(response, 'User not found')

    def test_find_user_redirects(self):
        response = self.client.get(reverse('lastfm:find_user'), {'username': 'rj'})
        self.assertRedirects(response, '/user/rj/', fetch_redirect_response=False)

    @patch('lastfm.views.requests.get')
    def test_weekly_chart(self, mock_get):
        mock_get.side_effect = fake_api({
            'user.getweeklyartistchart': WEEKLY_ARTISTS,
            'user.getweeklytrackchart': WEEKLY_TRACKS,
        })
        response = self.client.get(reverse('lastfm:weekly_chart', args=['rj']))
        self.assertContains(response, 'Radiohead')
        self.assertContains(response, 'Creep')
