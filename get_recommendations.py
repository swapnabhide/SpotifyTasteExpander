import spotipy
# from pprint import pprint 

from utils.config import access_token

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id, client_secret,scope=["user-library-read", "user-top-read"], redirect_uri="http://localhost:8080"))

# track = sp.search(q='track:Scream artist:Momentum', type='track')
# pprint(track)


client_id='2dd429303f8a4cfbb08ba7996a356f32'
client_secret="e568514a2ea74409a8623ddd1f92351e"


import base64
import requests

# Set up API endpoint and parameters
# url = 'https://accounts.spotify.com/api/token'
# params = {'grant_type': 'authorization_code'}
# call_back_url = 'https://developer.spotify.com/callback'
# # Set up authorization headers
# auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()
# headers = {'Authorization': f'Basic {auth_header}'}

# # Make the API request
# response = requests.post(url, params=params, headers=headers)

# print(response.status_code, response.reason, response.text)
# # Extract the access token from the response
# access_token = response.json()['access_token']
# print(access_token)


# Set up the API authorization headers
headers = {'Authorization': f'Bearer {access_token}'}
# Set up the API endpoint and parameters
url = 'https://api.spotify.com/v1/search'
params = {'q': 'track:Scream artist:Momentum', 'type': 'track', 'limit': 1}
# Make the API request
response = requests.get(url, params=params, headers=headers)
print(response.reason)
# Extract the track ID from the response data
track_id = response.json()['tracks']['items'][0]['id']

# Set up the API endpoint and parameters for track analysis
url = f'https://api.spotify.com/v1/audio-analysis/{track_id}'

# Make the API request for track analysis
response = requests.get(url, headers=headers)

# Extract the number of plays from the response data
num_plays = response.json()['track']['num_samples']

# Print the number of plays
print(f'The track "Scream" by Momentum has been played {num_plays} times on Spotify.')
