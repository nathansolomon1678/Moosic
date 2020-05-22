# I have no clue what I am doing
import os
import spotipy
user_id = "1knaig961apydoe6jjdhwyiq6"
with open('api_key.txt') as file:
    api_key = file.read()
os.system(f'curl -X "GET" "https://api.spotify.com/v1/users/{user_id}/playlists" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {api_key}"')
