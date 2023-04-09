from utils.config import client_secret, client_id, redirect_uri
import spotipy
from spotipy.oauth2 import SpotifyOAuth



def init_spotify(scope):
        return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id,
            client_secret,
            scope=scope,
            redirect_uri=redirect_uri
            )
        )
