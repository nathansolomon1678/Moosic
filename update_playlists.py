#!/usr/bin/env python3
""" Updates the local copies of playlists

Those changes are saved in the playlists/ directory """
import json
import os
import spotipy
import re
from typing import List, Dict, Any, Tuple

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

def same_song(song1: Dict[str, Any], song2: Dict[str, Any]) -> bool:
    """ Given two songs (each as dictionaries containing the title and artists),
    returns whether the songs are the same, even if they have different IDs """
    # List of all artists for each song:
    artists: List[List[str]] = [song['Artists'] for song in [song1, song2]]
    artists_overlap: bool = len(set(artists[0]).intersection(set(artists[1]))) > 0
    # The pattern ' - ' is usually followed by 'Remastered <year>' or 'Radio edit' or something
    titles: List[str] = [song['Title'].split(' - ')[0] for song in [song1, song2]]
    # Also, anything enclosed in parentheses is unnecessary
    titles = [re.sub('\(.*\)', '', title) for title in titles]
    titles = [re.sub('\[.*\]', '', title) for title in titles]
    titles = [title.rstrip() for title in titles]
    return artists_overlap and titles[0] == titles[1]

def get_playlist(playlist_id: str, sort=True) -> List[Dict[str, Any]]:
    """ Returns useful information for each song on a playlist """
    songs = []
    offset = 0
    # Retrieve 100 songs at a time until there aren't any left
    while True:
        # The offset tells it which index to start at
        fields="items.track.name, items.track.id, items.track.artists.name, items.track.duration_ms"
        new_songs = s.playlist_items(playlist_id, fields=fields, offset=offset, limit=100)['items']
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

def get_playlist_name(id):
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
    main_playlist_name = get_playlist_name(main)
    songs = get_playlist(main)
    for feeder in feeders:
        feeder_name = get_playlist_name(feeder)
        new_songs = []
        for new_song in get_playlist(feeder):
            if True not in [same_song(new_song, existing_song) for existing_song in songs]:
                new_songs.append(new_song)
                songs.append(new_song)
        add_songs(main, [song['ID'] for song in new_songs])
        print(f'\033[0;1mCopied {len(new_songs)} new songs from "{feeder_name}" to "{main_playlist_name}":')
        for song in new_songs:
            print(f'\033[0;32m{song}')
    # TODO: automatically remove dupes or songs that are no longer on any feeder playlists (and print warning that songs are being removed)

def warn_of_dupes(songs: List[Dict[str, Any]], playlist_name: str) -> None:
    """ Given a list of songs, prints any that appear to be duplicates """
    # It would be really nice to use sets here, but dictionaries are unhashable, so we can't
    unique_songs = []
    # Instead of printing dupes, store them in a list, to be counted and then printed
    dupes_to_print = []
    for new_song in songs:
        for existing_song in unique_songs:
            if same_song(new_song, existing_song):
                dupes_to_print.append(f'\033[0;31m{new_song}\033[0;35m (similar to\n{existing_song})\n')
                break
        unique_songs.append(new_song)
    print(f'\033[0;1mFound {len(dupes_to_print)} duplicate songs in "{playlist_name}":')
    for thing_to_print in dupes_to_print: print(thing_to_print)

# Dictionary of main playlists to feeders for each of those
# For example, the ID of a family playlist is the key to the IDs of individual playlists for each family member
feeder_playlists = {
    '6PR9WVuDfnp98ZxvqTvdyy': [
        '6vxJkWv5QjBCWuMUU11Yu0',
        '496qzGOJjyhvnAkGS7Z5nR',
        '0nIOYMhTBQDrGwrvCc6TUW',
        '6vDwFEEeqByv0EdEpgX0LR',
        '7A3XejLvWvSmIX2yGQPCJ5',
        '66IDHTnc0e2RkqsMSyFHu3',
        '1LlrlIzlZVzNEqz1FOeuZh',
    ],
}

for main, feeders in feeder_playlists.items():
    copy(main, feeders)

playlists_to_version_control = {
    # This is not all of my playlists. Only the essential ones.
    '496qzGOJjyhvnAkGS7Z5nR',
    '6PR9WVuDfnp98ZxvqTvdyy',
    '1DpbunhpYFcYAPzkZYNuJk',
    '67IYsx9XFi5m8h5BKU3RSm',
    '77OoDDnU6VIIaBuY3f5abq',
    '6ABDcWlzwBt0H1rh4PZby4',
    '0rffpWauvb1LYb3lU7nesG',
    '3kZEyyQVquZesT40A6v8aB',
    '5lT8LaIV1V6crhwqilYKKr',
    '6J2SpAqypYRarlDgnmeMRT',
}

os.system('rm -rf playlists')
os.mkdir('playlists')
for playlist in playlists_to_version_control:
    songs = get_playlist(playlist)
    playlist_name = get_playlist_name(playlist)
    warn_of_dupes(songs, playlist_name)
    file = open(f'playlists/{playlist_name}', 'w')
    for song in songs:
        file.write(f'{str(song)}\n')
    file.close()
print('\033[0;0m')  # Reset to normal output color & format

print('\033[0;36mSuccessfully updated playlists! Use "git diff HEAD~" to see most recent changes. To save changes to the cloud, add & commit & push.')
