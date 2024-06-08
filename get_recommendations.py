from datetime import datetime
import random
import spotipy

from spotify_auth import init_spotify

sp = init_spotify(scope=["user-library-read", "user-top-read", "playlist-modify-private", "playlist-modify-public", "playlist-read-private"])

def get_user_liked_songs(sp):
    results = sp.current_user_saved_tracks()
    return [item['track']['id'] for item in results['items']]

def get_top_tracks(sp, limit=20, time_range='long_term'):
    return [item['id'] for item in sp.current_user_top_tracks(limit=limit, time_range=time_range)['items']]

def get_recommended_tracks(sp, seed_artists, seed_tracks):
    try:
        recommendations = sp.recommendations(seed_artists=seed_artists, seed_tracks=seed_tracks,
                                        limit=20, max_popularity=100, min_popularity=0)
        return [track['id'] for track in recommendations['tracks']]
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error fetching recommendations: {e}")
        exit (1)
def get_user_top_artists(sp, limit=50, time_range='long_term'):
    return [item['id'] for item in sp.current_user_top_artists(limit=limit, time_range=time_range)['items']]

def get_random_tracks(sp, similar_tracks):
    # get 50 random tracks from new releases with artists I don't listen to one song per artist
    random_tracks = []
    explored_artist = []
    explored_artist.extend(get_user_top_artists(sp))
    while len(random_tracks) < 50:  # Adjust number as needed
        results = sp.new_releases(limit=50)
        for item in results['albums']['items']:
            album_tracks = sp.album_tracks(item['id'])
            for track in album_tracks['items']:
                if track['id'] not in similar_tracks and track['id'] not in random_tracks and track['artists'][0]['id'] not in explored_artist:
                    random_tracks.append(track['id'])
                    explored_artist.append(track['artists'][0]['id'])
            if len(random_tracks) >= 50:
                break
    return random_tracks

def create_playlist(sp, track_ids):
    user_id = sp.current_user()['id']
    date = datetime.now().strftime("%Y-%m-%d")
    playlist = sp.user_playlist_create(user_id, f'Non-Similar Songs Playlist {date}', public=False)
    sp.user_playlist_add_tracks(user_id, playlist['id'], track_ids)
    return playlist['external_urls']['spotify']

def main():
    songs_in_taste = get_user_liked_songs(sp)
    songs_in_taste.extend(get_top_tracks(sp))
    seed_artists = []
    seed_tracks = []
    for track in songs_in_taste:
        seed_tracks.append(track)
        artists = sp.track(track)['album']['artists']
        seed_artists.extend(artist['id'] for artist in artists)
    songs_in_taste.append(
        get_recommended_tracks(
            sp, seed_artists=random.sample(seed_artists, min(len(seed_artists), 3)), seed_tracks=random.sample(seed_tracks, min(len(seed_tracks), 2))
        )
    )
    random_tracks = get_random_tracks(sp, songs_in_taste)
    playlist_url = create_playlist(sp, random_tracks)
    print(f"Playlist created: {playlist_url}")


if __name__ == "__main__":
    main()