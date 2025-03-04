from Spotify import SpotifyAPI
response = SpotifyAPI().search('All of the lights Kanye West')

track = response['tracks']['items'][0]['name']
artist = response['tracks']['items'][0]['artists'][0]['name']
track_id = response['tracks']['items'][0]['id']


from Spotify import DB

DB().get_playlist_df(DB().Spot_playlist_id)['track_id']

import json
from YouTube import YouTubeAPI
YouTubeAPI().YT_playlist
#response = YouTubeAPI().get_playlist_info()
#response = response.json()

#with open(r"C:\Users\kwamr\OneDrive\Desktop\SpotifyYouTubeProject\output.json", "w") as file:
#    file = file.write(json.dumps(response, indent=4))


with open(r"C:\Users\kwamr\OneDrive\Desktop\SpotifyYouTubeProject\output.json", "r") as file:
    response = json.loads(file.read())
response['items'][0]['snippet']['title']


for i in range(len(response['items'])):
    playlist_list_id = response['items'][i]['id']
    song = response['items'][i]['snippet']['title']
    song = song.lower().replace("official video","").replace("()","").strip()
    response['items'][1]
    if response['items'][1]['id'] not in DB().get_playlist_df(DB().Spot_playlist_id)['playlist_list_id'].values:
        response = SpotifyAPI().search(song)


with open(r"spot.json", "r", encoding="utf-8") as file:
    new_response = json.loads(file)
file.close()
new_response
#grab YouTube playlist
#grab SpotifyDB  
#if new YouTube playlist_list_id not in SpotifyDB
    #grab YouTube title + YouTube channel name 
    #search spotify for song name 
    #find closest match using regex search 
    #insert song details into SpotifyDB 
    #add track_id to Spotify playlist 
    #insert playlist_list_id into SpotifyDB 
    

#if YouTube playlist_list_id in SpotifyDB but not in YouTube playlist 
    #remove playlist_list_id item from YouTube playlist 
    #remove song from SpotifyDB
    #remove song from SpotifyAPI playlist 