#!/usr/bin/env python3
import utils

playlist = '496qzGOJjyhvnAkGS7Z5nR'
songs = utils.get_playlist(playlist)
playlist_name = utils.get_playlist_name(playlist)
utils.warn_of_dupes(songs, playlist_name)
