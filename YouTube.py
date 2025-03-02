import pandas as pd, sys, requests, json, requests, os, subprocess, regex
#YouTube API configuration 

# ---> YouTube OAuth 2.0 configuration 
#Once we have the unique video id we will add the video to a private playlist 
#This action will require OAuth 2.0 token because we are accessing/modifying private user data
import googleapiclient.discovery,  google_auth_oauthlib.flow, googleapiclient.errors 
from google.oauth2 import credentials


class YouTubeAPI:
    def __init__(self):
        with open(os.getcwd()+r"\\API keys + refresh tokens\\" + "YouTubeAPI.json") as f: 
            YouTube_API_json = json.load(f)
        self.YouTube_API_key = YouTube_API_json['API']
        self.KD_channel = 'UCvhiKXH8XeOo3cQePeFwjpg'
        self.YT_playlist ='PL3qmZgAqUhzaEzdV_Cl9dhPn9K9B2CGTS'



    def search(self, track, artist, duration):
        if type(track) != str:
            track = track.str.replace("'","''")
        else:
            track.replace("'","''")
        if type(artist) != str:
            artist = artist.str.replace("'","''")
        else: 
            artist = artist.replace("'","''")
        #add search query parameters including the track name and artist and duration 
        keyword = f"{track} {artist}".replace(" ", "+")
        if duration/(1000*60) < 4:
            run_time = "short"
        else:
            run_time = "medium"
        YT_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q={keyword}&type=video&videoDuration={run_time}&key={self.YouTube_API_key}"
        YT_response = requests.get(YT_url)
        print(YT_response)
        YT_dump = YT_response.json()
            #Match the artist to the channel title if the channel title has the artist name in it
        k = 0   
        video_id = ''
        while k < len(YT_dump["items"]):
            channel_titles = YT_dump["items"][k]["snippet"]["channelTitle"]
            track_names = YT_dump["items"][k]["snippet"]["title"]
            artist_regex_pattern = f"({artist.lower()}){{e<=2}}"
            artists_regex_match = regex.findall(artist_regex_pattern, channel_titles.lower())
            #print(artists_regex_match)
            track_regex_pattern = f"({track.lower()}){{e<=2}}"
            track_regex_match = regex.findall(track_regex_pattern, track_names.lower())
            #print(track_regex_match)
            #the accuracy of the below fuzzy matching decreases as the length of the track name increases 
            #therefore if the length of the track name exceeds 40 characters the first observation will be selected
            if len(track) >= 40: 
                video_id += YT_dump["items"][0]["id"]["videoId"]
                k += len(YT_dump['items'])
            elif (len(artists_regex_match) > 0) & (len(track_regex_match) > 0): 
                video_id += YT_dump["items"][k]["id"]["videoId"]
                k += len(YT_dump['items'])
            else:
                k += 1
        #if all else fails then set to inital YouTube observation 
        if video_id == '':
            video_id += YT_dump["items"][0]["id"]["videoId"] 
        return video_id

    #Note that this method only works for tracking public playlists on my channel
    def get_playlist_id(self, playlist_name): 
        get_all_playlists = f'https://www.googleapis.com/youtube/v3/playlists?part=snippet&maxResults=5&channelId={self.KD_channel}&key={self.YouTube_API_key}'
        playlist_pool = requests.get(get_all_playlists).json()
        #for potential searches you can refer to the playlist_ref database
        #DB().conn.cursor().execute("SELECT * FROM spotify.playlist_ref pr where TRIM(pr.YT_id) = ''").fetchall() 
        for i in range(len(playlist_pool['items'])):
            YT_playlist_title = playlist_pool['items'][0]['snippet']['title']
            YT_playlist_id = playlist_pool['items'][0]['id']
            playlist_regex_pattern = f"({playlist_name.lower()}){{e<=2}}"
            playlist_regex_match = regex.findall(playlist_regex_pattern, YT_playlist_title)
            x = 0
            while x == 0: 
                if len(playlist_regex_match) > 0: 
                    response = [YT_playlist_title, YT_playlist_id]
                else: 
                    break
        return response


    #Ideally this would be a private method, but I can't get that configured so therefore this method remains public
    def refresh_token(self, **kwargs):
        import json, requests
        token_path = os.getcwd()+r"\\API keys + refresh tokens\\" + "refresh_token_YouTube.json"
        with open(token_path) as f:
            YT_token = json.load(f)
        refresh_token = kwargs.get("Refresh Token", YT_token['refresh_token'])
        client_id = kwargs.get("Client ID", YT_token['client_id'])
        client_secret = kwargs.get("Client Secret", YT_token['client_secret'])
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": client_id,  # Replace with your client ID
            "client_secret": client_secret,  # Replace with your client secret
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()["access_token"]

    def grant_access(self):
        path = os.getcwd()+r"\\API keys + refresh tokens\\" +"client_secret_780748469530-6q5rid6ai4mh1rqgo6qt97tbmjt5iui0.apps.googleusercontent.com.json"
        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl","https://www.googleapis.com/auth/youtube","https://www.googleapis.com/auth/youtubepartner"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(path, scopes)
        creds = flow.run_local_server(port=8080) 
        print('Grant access')
        with open(os.getcwd()+r"\\API keys + refresh tokens\\" + "refresh_token_YouTube.json", 'w') as token:
            token.write(creds.to_json())
        input('Press enter if access was granted')
        token_path = os.getcwd()+r"\\API keys + refresh tokens\\" + "refresh_token_YouTube.json"
        with open(token_path) as f:
            YT_token = json.load(f)
        YT_token = YT_token['refresh_token']
        self.YT_token = YT_token
        #I am perplexed by the fetch_token 
        return YT_token

    def insert_video(self, YT_video_id, YT_playlist_id): 
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet"
        headers = {
            "Authorization": f"Bearer {YouTubeAPI().refresh_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json"
            }

        data = {
            "snippet": {
                "playlistId": YT_playlist_id,
                "resourceId": {"kind": "youtube#video",
                    "videoId": YT_video_id
                }
            }
        }
        response =  requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()
        #https://developers.google.com/youtube/v3/docs/playlistItems#resource

    def remove_video(self, YT_playlist_list_id): 
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?id={YT_playlist_list_id}"
        headers = {
            "Authorization": f"Bearer {YouTubeAPI().refresh_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json"
            }
        response = requests.delete(url, headers=headers)
        return response