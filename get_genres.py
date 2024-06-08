# get all genres on spotify
import json
import numpy as np
from spotify_auth import init_spotify
from pprint import pprint
import random


def get_seed_genres():
    sp = init_spotify(scope=["user-library-read", "user-top-read"])
    return sp.recommendation_genre_seeds()['genres']

def get_top_tracks(limit=100, time_range='medium_term'):
    sp = init_spotify(scope=["user-library-read", "user-top-read"])
    return sp.current_user_top_tracks(limit=limit, time_range=time_range)

def get_tracks_analytics(): 
    sp = init_spotify(scope=["user-library-read", "user-top-read"])
    top_tracks = get_top_tracks()
    track_ids = [track['id'] for track in top_tracks['items']]

    audio_features = sp.audio_features(track_ids)

    # Define a list of audio feature names to plot
    audio_feature_names = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

    # Create a separate graph for each audio feature
    for feature_name in audio_feature_names:
        feature_values = [feature[feature_name] for feature in audio_features]
        # Calculate the mean and standard deviation of the feature values
        mean = np.mean(feature_values)
        std_dev = np.std(feature_values)

        # Define a range based on the mean and standard deviation
        range_start = mean - std_dev
        range_end = mean + std_dev

        print(f"The range of {feature_name} values for most tracks is {range_start:.2f} to {range_end:.2f}")


def get_recommended_tracks():
    sp = init_spotify(scope=["user-library-read", "user-top-read"])
    top_tracks = get_top_tracks(limit=100, time_range='long_term')
    print(len(top_tracks['items']))
    print()
    
    seed_artists = []
    seed_tracks = []
    seed_tracks = seed_tracks.extend(top_tracks['items'][random.randint(0,20)]['id'])
    artists = top_tracks['items'][random.randint(0,20)]['album']['artists']
    seed_artists.extend(artist['id'] for artist in artists)
    # seed_artists = [artists.extend(tracks['artists']['id']) for tracks in top_tracks] 
    print(seed_artists)
    print(seed_tracks)
    # Get the recommended tracks with a maximum popularity of 100 and a minimum popularity of 99
    recommendations = sp.recommendations(seed_artists=seed_artists, seed_tracks=seed_tracks,
                                        limit=20, max_popularity=100, min_popularity=0)

    # Print the recommended track names and popularity values
    for track in recommendations['tracks']:
        album_id = track['album']['id']
        album = sp.album(album_id)
        artist_id = album['artists'][0]['id']
        artist = sp.artist(artist_id)
        genres = artist['genres']
        print(track['name'], track['popularity'], genres)

def get_song_info_from_playlist(playlist_id):
    sp = init_spotify(scope=["user-library-read", "user-top-read"])
    res = sp.playlist_items(playlist_id)
    get_songs_info(sp, res['items'])

def get_songs_info(sp, items):
    """get name, album, polpularity, genre (if available)

    Args:
        sp (_type_): _description_
        items (_type_): _description_
    """
    track_info = {}
    for track in items:
        track_info["name"] = track['track']['name']
        track_info["Album"] = track['track']['album']['name']
        track_info["popularity"] = track['track']['popularity']
        artist_id = track['track']['artists'][0]['id']
        artist = sp.artist(artist_id)
        track_info["genres"] = artist['genres']

        print(track_info)
## Scream by Momentum
## Piece of Me by Lady Wray
## Close by Loveday
## Tell Me by Groove Theory

if __name__ == "__main__":
    # get_recommended_tracks()
    get_tracks_analytics()
    # get_song_info_from_playlist("37i9dQZEVXcRqBD8RsC3Qw")