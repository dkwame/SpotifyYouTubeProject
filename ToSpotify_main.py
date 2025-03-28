from Spotify import SpotifyAPI, DB
import json
response = SpotifyAPI().search('All of the lights Kanye West')

track = response['tracks']['items'][0]['name']
artist = response['tracks']['items'][0]['artists'][0]['name']
track_id = response['tracks']['items'][0]['id']


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


#from search API response
with open(r"spot.json", encoding="utf-8") as file:
    spot_response = json.load(file)
file.close()
spot_response

#from API list playlist items response
with open(r"output.json", encoding="utf-8") as file: 
    YT_response = json.load(file)
file.close()
YT_response

#if song in YouTube playlist, but playlist_list_id not in SpotifyDB() 
    # then grab song title from YouTube API and insert into SpotifyAPI 
    # from the SpotifyAPI response insert the track_id into the SpotifyAuth() using the SpotifyAPI/SpotifyAUth.insert_song(track_id,DB().playlist_id)

#from postgres dataframe
DB().get_playlist_df(DB().Spot_playlist_id)


YT_response['items'][0]

#grab YouTube playlist --> YouTubeAPI().get_playlist_info() ---> output.json()
for i in range(len(YT_response['items'])):
    YT_video_playlist_list_id =  YT_response['items'][i]['id'] 
    if YT_video_playlist_list_id not in DB().get_playlist_df(DB().Spot_playlist_id)['playlist_list_id'].values:
       song = YT_response['items'][i]['snippet']['title']
       song = song.lower().replace("official video","").replace("()","").strip()
       #spot_response = SpotifyAPI().search(song)
       spot_track_id = spot_response['tracks']['items'][0]['id']
    else: 
        continue
    #insert song details into SpotifyDB 
    #add track_id to Spotify playlist 
    #insert playlist_list_id into SpotifyDB 
    
spot_response['tracks']
#if YouTube playlist_list_id in SpotifyDB but not in YouTube playlist 
    #remove playlist_list_id item from YouTube playlist 
    #remove song from SpotifyDB
    #remove song from SpotifyAPI playlist 