# Spotify Taste Expander - Setup Guide

## Overview
This web application allows users to authenticate with their Spotify account and automatically create a playlist filled with songs they don't typically listen to, helping them expand their musical taste.

## Prerequisites
- Python 3.7 or higher
- A Spotify account
- Spotify Developer App credentials

## Setup Instructions

### 1. Get Spotify API Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app name and description (e.g., "Taste Expander")
5. Once created, note down your **Client ID** and **Client Secret**
6. Click "Edit Settings"
7. Add the following to **Redirect URIs**: `http://localhost:8080/callback`
8. Click "Save"

### 2. Configure the Application

1. Navigate to the `utils` directory:
   ```bash
   cd utils
   ```

2. Copy the config template:
   ```bash
   cp config_template.py config.py
   ```

3. Edit `config.py` and add your credentials:
   ```python
   client_id = "YOUR_CLIENT_ID_HERE"
   client_secret = "YOUR_CLIENT_SECRET_HERE"
   redirect_uri = "http://localhost:8080/callback"
   access_token = ""  # Leave empty for web app
   ```

### 3. Install Dependencies

Create a virtual environment and install required packages:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Run the Web Application

```bash
python app.py
```

The application will start on `http://localhost:8080`

### 5. Use the Application

1. Open your browser and navigate to `http://localhost:8080`
2. Click "Login with Spotify"
3. Authorize the application (you'll be redirected to Spotify)
4. After authorization, you'll be redirected back to the app
5. Click "Create My Playlist" to generate your taste-expanding playlist
6. The playlist will be created in your Spotify account and you'll get a link to open it

## How It Works

The application:
1. Analyzes your saved tracks and top artists
2. Gets Spotify's recommendations based on your listening history
3. Filters out these familiar songs
4. Finds new releases from artists you haven't explored
5. Creates a private playlist with 50 fresh tracks

## Troubleshooting

### "No module named 'utils.config'"
Make sure you've created `utils/config.py` from the template and added your credentials.

### "Invalid redirect URI"
Ensure that `http://localhost:8080/callback` is added to your Spotify app's Redirect URIs in the dashboard.

### "Insufficient client scope"
The app requires the following scopes:
- user-library-read
- user-top-read
- playlist-modify-private
- playlist-modify-public
- playlist-read-private

These are automatically requested during login.

### Not enough tracks found
If you're a new Spotify user with limited listening history, the app might not find enough tracks. Try listening to more music and try again later.

## Security Notes

- Never commit `utils/config.py` to version control (it's in .gitignore)
- Keep your Client Secret private
- The app uses session-based authentication for security
- All playlists are created as private by default

## Development

To run in development mode with debug enabled:
```bash
python app.py
```

The Flask app runs with `debug=True` by default, which enables auto-reload when you make changes.

## Next Steps

- Customize the playlist generation algorithm in `app.py`
- Adjust the number of tracks (currently set to 50)
- Modify the filtering criteria for songs
- Add more user preferences and options
