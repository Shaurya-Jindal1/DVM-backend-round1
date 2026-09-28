import requests
from datetime import datetime

from django.conf import settings
from django.shortcuts import render, redirect

API_URL = 'https://ws.audioscrobbler.com/2.0/'


def call_api(params):
    """sends a request to the last.fm api and returns the json"""
    params['api_key'] = settings.LASTFM_API_KEY
    params['format'] = 'json'
    try:
        response = requests.get(API_URL, params=params)
        return response.json()
    except Exception as e:
        print('Error calling last.fm api:', e)
        return {'error': 0, 'message': 'Could not connect to Last.fm, please try again later'}


def get_image(images):
    # last.fm sends a list of images (small, medium, large, extralarge)
    # index 2 is the large one
    try:
        return images[2]['#text']
    except (IndexError, KeyError, TypeError):
        return ''


def home(request):
    return render(request, 'lastfm/home.html')


def top_charts(request):
    country = request.GET.get('country', '').strip()
    chart_type = request.GET.get('type', 'artists')
    page = int(request.GET.get('page', 1))

    context = {
        'country': country,
        'type': chart_type,
        'page': page,
    }

    if not country:
        return render(request, 'lastfm/charts.html', context)

    results = []
    if chart_type == 'tracks':
        data = call_api({'method': 'geo.gettoptracks', 'country': country, 'page': page, 'limit': 20})
        if 'error' in data:
            context['error'] = data['message']
            return render(request, 'lastfm/charts.html', context)

        for track in data['tracks']['track']:
            results.append({
                'name': track['name'],
                'artist': track['artist']['name'],
                'listeners': track['listeners'],
                'url': track['url'],
                'image': get_image(track['image']),
            })
        total_pages = int(data['tracks']['@attr']['totalPages'])
    else:
        data = call_api({'method': 'geo.gettopartists', 'country': country, 'page': page, 'limit': 20})
        if 'error' in data:
            context['error'] = data['message']
            return render(request, 'lastfm/charts.html', context)

        for artist in data['topartists']['artist']:
            results.append({
                'name': artist['name'],
                'listeners': artist['listeners'],
                'url': artist['url'],
                'image': get_image(artist['image']),
            })
        total_pages = int(data['topartists']['@attr']['totalPages'])

    context['results'] = results
    context['total_pages'] = total_pages
    return render(request, 'lastfm/charts.html', context)


def search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'artist')
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    context = {
        'query': query,
        'type': search_type,
        'page': page,
    }

    if query == '':
        return render(request, 'lastfm/search.html', context)

    if search_type == 'album':
        data = call_api({'method': 'album.search', 'album': query, 'page': page, 'limit': 20})
    elif search_type == 'track':
        data = call_api({'method': 'track.search', 'track': query, 'page': page, 'limit': 20})
    else:
        search_type = 'artist'
        data = call_api({'method': 'artist.search', 'artist': query, 'page': page, 'limit': 20})

    if 'error' in data:
        context['error'] = data['message']
        return render(request, 'lastfm/search.html', context)

    results = []
    matches = data['results'][search_type + 'matches'][search_type]
    for item in matches:
        result = {
            'name': item['name'],
            'url': item['url'],
            'image': get_image(item.get('image')),
        }
        # albums and tracks have an artist, artists and tracks have listeners
        if 'artist' in item:
            result['artist'] = item['artist']
        if 'listeners' in item:
            result['listeners'] = item['listeners']
        results.append(result)

    total = int(data['results']['opensearch:totalResults'])
    context['results'] = results
    context['total'] = total
    context['total_pages'] = total // 20 + 1
    return render(request, 'lastfm/search.html', context)


def artist_page(request, name):
    data = call_api({'method': 'artist.getinfo', 'artist': name, 'autocorrect': 1})
    if 'error' in data:
        return render(request, 'lastfm/artist.html', {'error': data['message'], 'name': name})

    artist = data['artist']
    info = {
        'name': artist['name'],
        'url': artist['url'],
        'image': get_image(artist['image']),
        'listeners': artist['stats']['listeners'],
        'playcount': artist['stats']['playcount'],
        'bio': artist['bio']['summary'],
        'tags': artist['tags']['tag'],
        'similar': artist['similar']['artist'],
    }

    top_tracks = []
    tracks_data = call_api({'method': 'artist.gettoptracks', 'artist': artist['name'], 'limit': 10})
    if 'error' not in tracks_data:
        for track in tracks_data['toptracks']['track']:
            top_tracks.append({
                'name': track['name'],
                'playcount': track['playcount'],
                'url': track['url'],
            })

    return render(request, 'lastfm/artist.html', {'artist': info, 'top_tracks': top_tracks})


# ---------- user profiles (extra feature) ----------

def find_user(request):
    # the form on the home page sends the username here
    username = request.GET.get('username', '').strip()
    if username:
        return redirect('/user/' + username + '/')
    return redirect('lastfm:home')


def user_profile(request, username):
    period = request.GET.get('period', '7day')

    user_data = call_api({'method': 'user.getinfo', 'user': username})
    if 'error' in user_data:
        return render(request, 'lastfm/user.html', {'error': user_data['message'], 'username': username})

    user = user_data['user']
    profile = {
        'name': user['name'],
        'realname': user.get('realname', ''),
        'url': user['url'],
        'image': get_image(user['image']),
        'country': user.get('country', ''),
        'playcount': user['playcount'],
        'artist_count': user.get('artist_count', ''),
        'registered': datetime.fromtimestamp(int(user['registered']['unixtime'])),
    }

    # top artists
    top_artists = []
    data = call_api({'method': 'user.gettopartists', 'user': username, 'period': period, 'limit': 10})
    if 'error' not in data:
        for artist in data['topartists']['artist']:
            top_artists.append({
                'name': artist['name'],
                'playcount': artist['playcount'],
                'image': get_image(artist['image']),
            })

    # top tracks
    top_tracks = []
    data = call_api({'method': 'user.gettoptracks', 'user': username, 'period': period, 'limit': 10})
    if 'error' not in data:
        for track in data['toptracks']['track']:
            top_tracks.append({
                'name': track['name'],
                'artist': track['artist']['name'],
                'playcount': track['playcount'],
            })

    # recent tracks
    recent_tracks = []
    data = call_api({'method': 'user.getrecenttracks', 'user': username, 'limit': 10})
    if 'error' not in data:
        for track in data['recenttracks']['track']:
            t = {
                'name': track['name'],
                'artist': track['artist']['#text'],
                'album': track['album']['#text'],
                'image': get_image(track['image']),
                'now_playing': False,
                'date': '',
            }
            # the song that is playing right now has no date, it has @attr nowplaying instead
            if '@attr' in track and track['@attr'].get('nowplaying') == 'true':
                t['now_playing'] = True
            if 'date' in track:
                t['date'] = track['date']['#text']
            recent_tracks.append(t)

    periods = [
        ('7day', 'Last 7 days'),
        ('1month', 'Last month'),
        ('3month', 'Last 3 months'),
        ('6month', 'Last 6 months'),
        ('12month', 'Last year'),
        ('overall', 'All time'),
    ]

    context = {
        'username': username,
        'profile': profile,
        'top_artists': top_artists,
        'top_tracks': top_tracks,
        'recent_tracks': recent_tracks,
        'period': period,
        'periods': periods,
    }
    return render(request, 'lastfm/user.html', context)


def weekly_chart(request, username):
    artist_data = call_api({'method': 'user.getweeklyartistchart', 'user': username})
    if 'error' in artist_data:
        return render(request, 'lastfm/weekly.html', {'error': artist_data['message'], 'username': username})

    track_data = call_api({'method': 'user.getweeklytrackchart', 'user': username})

    artists = []
    for artist in artist_data['weeklyartistchart']['artist'][:20]:
        artists.append({'name': artist['name'], 'playcount': artist['playcount']})

    tracks = []
    if 'error' not in track_data:
        for track in track_data['weeklytrackchart']['track'][:20]:
            tracks.append({
                'name': track['name'],
                'artist': track['artist']['#text'],
                'playcount': track['playcount'],
            })

    attr = artist_data['weeklyartistchart']['@attr']
    context = {
        'username': username,
        'artists': artists,
        'tracks': tracks,
        'from_date': datetime.fromtimestamp(int(attr['from'])),
        'to_date': datetime.fromtimestamp(int(attr['to'])),
    }
    return render(request, 'lastfm/weekly.html', context)
