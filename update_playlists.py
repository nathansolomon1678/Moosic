#!/usr/bin/python
""" Updates the local copies of playlists

Those changes are saved in the playlists/ directory """
import json
import os
import spotipy
from typing import List, Dict, Any

with open('api_key_stuff.json') as file:
    info = json.load(file)
    token = spotipy.util.prompt_for_user_token(
        info['Username'],
        info['Scope'],
        info['Client ID'],
        info['Client Secret'],
        info['Redirect URI']
    )
s = spotipy.Spotify(auth=token)

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
    songs = [{'ID':            song['id'],
              'Title':         song['name'],
              'Artists':       [artist['name'] for artist in song['artists']],
              'Duration':      song['duration_ms'] / 1000,
             } for song in songs]
    if sort:
        # By default, sort alphabetically
        songs.sort(key = lambda song: song['Title'])
    return songs

def playlist_name(id):
    """ Returns the name of a playlist whose ID is given """
    return s.playlist(id, fields='name')['name']

def add_songs(playlist, songs):
    """ Given a playlist ID & a list of song IDs, adds all those songs to the playlist """
    # Can only add 100 at a time, so split songs into chunks of 100
    while len(songs) > 0:
        s.playlist_add_items(playlist, songs[:100])
        del songs[:100]

def copy(main, feeders):
    """ Copies all unique songs from feeder playlists to a main playlist """
    main_playlist_name = playlist_name(main)
    songs = {song['ID'] for song in get_playlist(main)}
    for feeder in feeders:
        feeder_name = playlist_name(feeder)
        new_songs = {song['ID'] for song in get_playlist(feeder)} - songs
        add_songs(main, list(new_songs))
        songs = songs.union(new_songs)
        print(f'Copied {len(new_songs)} new songs from "{feeder_name}" to "{main_playlist_name}"')

# Dictionary of main playlists to feeders for each of those
# For example, the ID of a family playlist is the key to the IDs of individual playlists for each family member
feeder_playlists = {
    '6PR9WVuDfnp98ZxvqTvdyy': [
        '6vxJkWv5QjBCWuMUU11Yu0',
        '496qzGOJjyhvnAkGS7Z5nR',
        '0nIOYMhTBQDrGwrvCc6TUW',
        '6vDwFEEeqByv0EdEpgX0LR',
    ],
}

for main, feeders in feeder_playlists.items():
    copy(main, feeders)

playlists_to_version_control = {
    '496qzGOJjyhvnAkGS7Z5nR',
    '6PR9WVuDfnp98ZxvqTvdyy',
}

os.system('rm -rf playlists')
os.mkdir('playlists')
for playlist in playlists_to_version_control:
    file = open(f'playlists/{playlist}', 'w')
    for song in get_playlist(playlist):
        file.write(f'{str(song)}\n')
    file.close()

print('Don\'t forget to commit and push these updates!  :)')
