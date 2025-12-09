# Spotify Taste Expander

A web application that helps you discover new music by creating personalized playlists filled with songs outside your usual listening habits. Break free from Spotify's recommendation bubble and expand your musical horizons!

## What It Does

Spotify Taste Expander analyzes your listening history and creates a playlist specifically designed to introduce you to music you wouldn't normally encounter:

1. **Analyzes your taste** - Reviews your saved tracks, top artists, and listening patterns
2. **Identifies your comfort zone** - Determines what Spotify typically recommends to you
3. **Finds fresh music** - Discovers new releases from artists you haven't explored yet
4. **Creates your playlist** - Automatically generates a private playlist with 50 hand-picked tracks

## Features

- **OAuth 2.0 Authentication** - Secure Spotify login with session management
- **Smart Filtering** - Excludes songs you already know and similar recommendations
- **Artist Diversity** - Ensures variety by limiting tracks per artist
- **Automatic Playlist Creation** - Creates dated playlists in your Spotify account
- **Web Interface** - Simple, user-friendly Flask-based UI
- **Error Handling** - Robust validation for users with limited listening history

## Quick Start

1. **Get Spotify API credentials** from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. **Configure the app** by copying `utils/config_template.py` to `utils/config.py` and adding your credentials
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run the app**: `python app.py`
5. **Open your browser** to `http://localhost:8080`

For detailed setup instructions, see [SETUP.md](SETUP.md).

## How It Works

The algorithm:
- Gathers your top 50 liked songs and top 20 tracks
- Collects Spotify's recommendations based on your taste
- Finds new releases from artists not in your listening history
- Filters out everything you already know or would typically discover
- Creates a playlist with 50 tracks that push your musical boundaries

## Requirements

- Python 3.7+
- Spotify account
- Spotify Developer App credentials

## Tech Stack

- **Flask** - Web framework
- **Spotipy** - Spotify Web API wrapper
- **OAuth 2.0** - Secure authentication

## Contributing

Feel free to submit issues or pull requests to improve the taste expansion algorithm or add new features!

## License

MIT License - feel free to use and modify as you wish.
