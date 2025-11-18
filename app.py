from flask import Flask, render_template, redirect, request, session, url_for
import os
from datetime import datetime
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from utils.config import client_id, client_secret, redirect_uri

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Spotify OAuth configuration
SCOPE = "user-library-read user-top-read playlist-modify-private playlist-modify-public playlist-read-private"

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        cache_path=None,  # Don't cache to disk for web app
        show_dialog=True
    )

def get_spotify_client():
    """Get authenticated Spotify client from session"""
    token_info = session.get('token_info', None)
    if not token_info:
        return None

    sp_oauth = get_spotify_oauth()

    # Check if token is expired and refresh if needed
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return spotipy.Spotify(auth=token_info['access_token'])

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Redirect user to Spotify authorization page"""
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback"""
    sp_oauth = get_spotify_oauth()
    session.clear()
    code = request.args.get('code')

    if not code:
        return "Error: No authorization code received", 400

    try:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        return redirect(url_for('create_playlist_page'))
    except Exception as e:
        return f"Error during authentication: {str(e)}", 500

@app.route('/create-playlist-page')
def create_playlist_page():
    """Page to initiate playlist creation"""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for('index'))

    try:
        user = sp.current_user()
        return render_template('create_playlist.html', user=user)
    except Exception as e:
        return f"Error fetching user info: {str(e)}", 500

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    """Create the taste-expanding playlist"""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for('index'))

    try:
        # Get user's liked songs
        songs_in_taste = []
        results = sp.current_user_saved_tracks(limit=50)
        songs_in_taste.extend([item['track']['id'] for item in results['items']])

        # Get top tracks
        top_tracks = sp.current_user_top_tracks(limit=20, time_range='long_term')
        songs_in_taste.extend([item['id'] for item in top_tracks['items']])

        # Get seed artists and tracks
        seed_artists = []
        seed_tracks = []
        for track_id in songs_in_taste[:10]:  # Limit to avoid too many API calls
            track = sp.track(track_id)
            seed_tracks.append(track_id)
            seed_artists.extend([artist['id'] for artist in track['artists']])

        # Get recommended tracks (songs to filter out)
        recommended_tracks = []
        if seed_artists and seed_tracks:
            recommendations = sp.recommendations(
                seed_artists=random.sample(seed_artists, min(len(seed_artists), 3)),
                seed_tracks=random.sample(seed_tracks, min(len(seed_tracks), 2)),
                limit=20
            )
            recommended_tracks = [track['id'] for track in recommendations['tracks']]

        songs_in_taste.extend(recommended_tracks)

        # Get user's top artists to exclude
        top_artists = sp.current_user_top_artists(limit=50, time_range='long_term')
        explored_artist = [item['id'] for item in top_artists['items']]

        # Get random tracks from new releases (excluding user's taste)
        random_tracks = []
        attempts = 0
        max_attempts = 10

        while len(random_tracks) < 50 and attempts < max_attempts:
            results = sp.new_releases(limit=50, offset=attempts * 50)
            for item in results['albums']['items']:
                album_tracks = sp.album_tracks(item['id'])
                for track in album_tracks['items']:
                    if (track['id'] not in songs_in_taste and
                        track['id'] not in random_tracks and
                        track['artists'][0]['id'] not in explored_artist):
                        random_tracks.append(track['id'])
                        explored_artist.append(track['artists'][0]['id'])

                if len(random_tracks) >= 50:
                    break
            attempts += 1

        # Create playlist
        user_id = sp.current_user()['id']
        date = datetime.now().strftime("%Y-%m-%d")
        playlist = sp.user_playlist_create(
            user_id,
            f'Taste Expander - {date}',
            public=False,
            description='Songs outside your usual taste to expand your musical horizons!'
        )

        # Add tracks to playlist (Spotify API allows max 100 tracks per request)
        if random_tracks:
            sp.user_playlist_add_tracks(user_id, playlist['id'], random_tracks)

        playlist_url = playlist['external_urls']['spotify']
        playlist_name = playlist['name']
        track_count = len(random_tracks)

        return render_template('success.html',
                             playlist_url=playlist_url,
                             playlist_name=playlist_name,
                             track_count=track_count)

    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
