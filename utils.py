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

def remove_songs(playlist, songs):
    """ Given a playlist ID & a list of song IDs, removes all those songs from the playlist """
    # Can only remove 100 at a time, so split songs into chunks of 100
    while len(songs) > 0:
        s.playlist_remove_all_occurrences_of_items(playlist, songs[:100])
        del songs[:100]

def copy(main, feeders):
    """ Copies all unique songs from feeder playlists to a main playlist, and removes songs that are no longer in any feeders """
    main_playlist_name = get_playlist_name(main)
    new_songs = []
    old_songs = get_playlist(main)
    for feeder in feeders:
        feeder_name = get_playlist_name(feeder)
        print(f'Fetching songs from "{feeder_name}" to copy to "{main_playlist_name}"')
        for new_song in get_playlist(feeder):
            unique = True
            for song in new_songs:
                if same_song(song, new_song):
                    unique = False
                    break
            if unique:
                new_songs.append(new_song)
    print(f'Removing old songs from "{main_playlist_name}"')
    remove_songs(main, [song['ID'] for song in old_songs])
    print(f'Adding {len(new_songs)} songs to "{main_playlist_name}"')
    add_songs(main, [song['ID'] for song in new_songs])

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

def restore_playlist(playlist_id):
    playlist_name = get_playlist_name(playlist_id)
    with open(f'playlists/{playlist_name}') as file:
        # This is not formatted as a JSON, so we have to extract the ID manually
        song_IDs = [line[8:30] for line in file.read().split('\n')]
    add_songs(playlist_id, song_IDs)
