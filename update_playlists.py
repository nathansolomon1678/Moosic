#!/usr/bin/env python3
""" Updates the local copies of playlists
Those changes are saved in the playlists/ directory """
from utils import *

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
        '698HwDsgYiBNKFZbL65j4w',
        '4PUiJEVFZoBpouVuKcJ5GR',
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
    '4PUiJEVFZoBpouVuKcJ5GR',
}

os.system('rm -rf playlists')
os.mkdir('playlists')
for playlist in playlists_to_version_control:
    songs = get_playlist(playlist)
    playlist_name = get_playlist_name(playlist)
    file = open(f'playlists/{playlist_name}', 'w')
    for song in songs:
        file.write(f'{str(song)}\n')
    file.close()
print('\033[0;0m')  # Reset to normal output color & format
print('\033[0;36mSuccessfully updated playlists! Use "git diff" to see most recent changes. To save changes to the cloud, add & commit & push.')

# TODO: check that all my liked songs are also in my miscellaneous playlist
