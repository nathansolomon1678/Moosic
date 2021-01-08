import json

with open('api_key_stuff.json', 'w') as file:
    info = {'Client ID':     input('Please enter your client ID:\n'),
            'Client Secret': input('Please enter your client secret:\n')}
    json.dump(info, file)
print('Done! Don\'t forget to run \'pip install spotipy\' if you haven\'t already.')
