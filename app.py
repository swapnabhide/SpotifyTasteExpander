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

        # If user has very little listening history, use medium_term and short_term too
        if len(songs_in_taste) < 10:
            top_tracks_medium = sp.current_user_top_tracks(limit=20, time_range='medium_term')
            songs_in_taste.extend([item['id'] for item in top_tracks_medium['items']])

            top_tracks_short = sp.current_user_top_tracks(limit=20, time_range='short_term')
            songs_in_taste.extend([item['id'] for item in top_tracks_short['items']])

        # Remove duplicates
        songs_in_taste = list(set(songs_in_taste))

        # Check if we have enough data
        if len(songs_in_taste) < 5:
            return render_template('error.html',
                error="You don't have enough listening history yet. Try listening to more music on Spotify and come back later!")

        # Get seed artists and tracks
        seed_artists = set()  # Use set to avoid duplicates
        seed_tracks = []
        for track_id in songs_in_taste[:20]:  # Check more tracks to get enough seeds
            try:
                track = sp.track(track_id)
                seed_tracks.append(track_id)
                for artist in track['artists']:
                    seed_artists.add(artist['id'])
            except Exception as e:
                print(f"Error fetching track {track_id}: {e}")
                continue

        seed_artists = list(seed_artists)

        # Get recommended tracks (songs to filter out)
        # Spotify API allows max 5 seeds total
        recommended_tracks = []
        if len(seed_artists) >= 2 and len(seed_tracks) >= 2:
            try:
                # Use up to 3 artists and 2 tracks (total 5 seeds max)
                num_artist_seeds = min(3, len(seed_artists))
                num_track_seeds = min(2, len(seed_tracks))

                recommendations = sp.recommendations(
                    seed_artists=random.sample(seed_artists, num_artist_seeds),
                    seed_tracks=random.sample(seed_tracks, num_track_seeds),
                    limit=20
                )
                recommended_tracks = [track['id'] for track in recommendations['tracks']]
            except Exception as e:
                print(f"Error getting recommendations: {e}")
                # Continue without recommendations if this fails

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
        import traceback
        error_details = f"{str(e)}\n\nIf this is a 404 error from the recommendations endpoint, it might be due to insufficient listening history or invalid seed data."
        print(f"Full error:\n{traceback.format_exc()}")
        return render_template('error.html', error=error_details)

@app.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
