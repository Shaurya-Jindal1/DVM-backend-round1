# DVM Backend Task 1 - Part B (Last.fm Explorer)

A Django website that uses the Last.fm API to show music data.

Made with Python 3.13, Django 6.1.1 and the `requests` library.

## Features

- **Top charts by country** - top artists or top tracks for any country (uses `geo.getTopArtists` and `geo.getTopTracks`)
- **Search** - search for artists, albums or tracks (uses `artist.search`, `album.search`, `track.search`)
- Results are paginated (20 per page)

### Extra feature: user profiles and artist pages

- Enter a Last.fm username to see their profile: total scrobbles, top artists and top tracks (you can change the time period), and their recently played tracks. If they are listening to something right now it shows "Now playing"
- Each user also has a weekly chart page with their top artists and tracks for the last week
- Clicking on an artist opens an artist page with their bio, tags, listener count, top tracks and similar artists

## How to run

1. Get an API key from https://www.last.fm/api/account/create
2. Make a file called `.env` in this folder (same folder as manage.py) and put your key in it:
   ```
   LASTFM_API_KEY=your_api_key_here
   ```
   (there's an example in `.env.example`)
3. Install everything and run the server:
   ```
   python -m venv .venv
   .venv\Scripts\activate        (on mac/linux: source .venv/bin/activate)
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```
4. Open http://127.0.0.1:8000/

Some things to try: country "India", search "believe", user "rj"

## Tests

```
python manage.py test
```

The tests mock `requests.get` so they don't actually call the Last.fm API (and don't need an API key).
