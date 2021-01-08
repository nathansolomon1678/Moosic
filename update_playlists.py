""" Updates the local copies of playlists

Those changes are saved in the playlists/ directory """
import json
import os
import spotipy
from typing import List, Dict, Any

with open('api_key_stuff.json') as file:
    info = json.load(file)
    os.environ["SPOTIPY_CLIENT_ID"]     = info['Client ID']
    os.environ["SPOTIPY_CLIENT_SECRET"] = info['Client Secret']
s = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials())

def get_playlist(playlist_id: str, sort=True) -> List[Dict[str, Any]]:
    """ Returns useful information for each song on a playlist """
    songs = []
    offset = 0
    while True:  # Retrieve 100 songs at a time until there aren't any left
        # The offset tells it which index to start at
        new_songs = s.playlist_items(playlist_id, offset=offset, limit=100)['items']
        offset += 100
        songs.extend(new_songs)
        if len(new_songs) < 100:
            break
    # Extract the useful information from everything Spotify gave
    songs = [song['track'] for song in songs]
    # This next line is only necessary because Eli Yasui took "There you go" off Spotify & I refuse to accept that
    songs = [song for song in songs if song is not None]
    songs = [{'Title':         song['name'],
              'Artists':       [artist['name'] for artist in song['artists']],
              'Duration':      song['duration_ms'] / 1000,
              'ID':            song['id'],
             } for song in songs]
    if sort:
        # By default, sort alphabetically
        songs.sort(key = lambda song: song['Title'])
    return songs

playlists_to_version_control = {
    '496qzGOJjyhvnAkGS7Z5nR',  # For now, I'll just be version controlling my main playlist
}
os.system('rm -rf playlists')
os.mkdir('playlists')
for playlist in playlists_to_version_control:
    file = open(f'playlists/{playlist}', 'w')
    file.write('[\n')
    for song in get_playlist(playlist):
        file.write(f'  {str(song)}\n')
    file.write(']')
    file.close()
