import requests, json, pandas as pd, os, pip, subprocess, sys
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
#Create definitions for the OAuth 2.0 configuration for both Spotify and YouTube 
#Spotify OAuth 2.0 configuration


class SpotifyAPI: 
    def __init__(self): 
        with open(os.getcwd()+r"\\API keys + refresh tokens\\" + "spotify_client_secret.json") as f:
            Spotify_Creds = json.load(f)
        self.redirect_uri = "https://localhost:8080"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.client_id = Spotify_Creds["web"]["client_id"]
        self.client_secret = Spotify_Creds["web"]["client_secret"]
        
    #kwargs was used just in case another client_id, client_secret, etc... was desired to be used
    #otherwise our default client_id, client_secret, etc... would be used 
    def refresh_token(self, **kwargs) -> str:
        client_id = kwargs.get('client_id',self.client_id)
        client_secret = kwargs.get('client_secret',self.client_secret)
        auth_url = kwargs.get('auth_url', self.auth_url)
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=auth_url, client_id=client_id,
                                client_secret=client_secret)
        return token["access_token"]

    def get_playlist_id(self, url: str) -> str:
        playlist_id = url.split('playlist/')[1]
        return playlist_id
    

    def get_playlist_info(self, playlist_id: str) -> json:
        import requests
        headers = {"Authorization": f"Bearer {SpotifyAPI().refresh_token()}"}
        response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}?market=US", headers=headers).json()
        # if response.code = 200 then:
        # self.data['Name'] = response.json() 
        return response

    def get_playlist_df(self, playlist_id: str): 
        import pandas as pd 
        response = SpotifyAPI().get_playlist_info(playlist_id)
        data = response['tracks']['items']
        Spotify_dict = {} 
        Spotify_dict["artist"] = []
        Spotify_dict["artist_id"] = []
        Spotify_dict["track"] = []
        Spotify_dict["track_id"] = []
        Spotify_dict["track URL"] = []
        Spotify_dict["duration"] = []
        Spotify_dict["date_added"] = []

        for i in range(len(data)):
            artist_id = data[i]["track"]["artists"][0]["id"]
            artist_path = data[i]["track"]["artists"][0]["name"]
            song_path = data[i]["track"]["name"]
            song_id = data[i]["track"]["id"]
            song_url = data[i]["track"]["external_urls"]["spotify"]
            song_duration = data[i]["track"]["duration_ms"]
            date_added = data[i]["added_at"][:10]
            Spotify_dict["artist"].append(artist_path)
            Spotify_dict["artist_id"].append(artist_id)
            Spotify_dict["track"].append(song_path)
            Spotify_dict["track_id"].append(song_id)
            Spotify_dict["duration"].append(song_duration)
            Spotify_dict["track URL"].append(song_url)
            Spotify_dict["date_added"].append(date_added)
            
        df = pd.DataFrame(Spotify_dict, columns=Spotify_dict.keys())
        return df

import keyring
import psycopg
class DB: 
#Create definitions for DB connections and actions 
#connect to the database
    def __init__(self):
        try:
            self.conn = psycopg.connect(dbname="postgres", user="postgres", password=keyring.get_password("postgres", "postgres"), host=keyring.get_password("postgres", "host"), port="5432", autocommit=True)
            #self.conn.autocommit = True
        except Exception as e:
            print(e)
        self.DB_cols = ['playlist_id', 'artist', 'artist_id', 'track', 'track_id','duration','date_added', 'video_id','playlist_list_id']

#connect_to_db().cursor().execute("SELECT * from spotify.playlist_ref").fetchall()

#if playlist reference table does not exist, create it. Making this a private method only because this should already be established
    def create_ref_playlist_table(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS Spotify.playlist_ref (playlist_id VARCHAR(200) primary key, playlist_name VARCHAR(200))")
        except Exception as e:
            print(e)
        cur.close()


#insert new playlist into the playlist reference table
    def insert_playlist_ref(self, playlist_id: str, playlist_name: str):
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO Spotify.playlist_ref (playlist_id, playlist_name) VALUES (%s, %s)", (playlist_id, playlist_name))
        except Exception as e:
            print(e)
            pass    
        cur.close()


#Create a table for the playlist details
    def create_playlist_table(self,playlist_id: str):
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"CREATE TABLE IF NOT EXISTS Spotify.playlist_{playlist_id} (playlist_id varchar(200), artist varchar(200), artist_id varchar(200), track varchar(200), track_id varchar(200) primary key, duration INT, date_added DATE, video_id varchar(200), playlist_list_id VARCHAR(75))")
        except Exception as e:
            print(e)        
        cur.close()

#insert new songs into the playlist table
    def insert_new_songs(self, playlist_id: str, new_songs: str):
        new_songs['track'] = new_songs['track'].str.replace("'","''")
        new_songs['artist'] = new_songs['artist'].str.replace("'","''")
        with self.conn.cursor() as cur:
            playlist_insert = f"INSERT INTO spotify.playlist_{playlist_id} "
            for i in range(len(new_songs)):
                try: 
                    cur.execute(playlist_insert + f"""(playlist_id, artist, artist_id, track, track_id, duration, date_added) VALUES 
                                ('{playlist_id}', '{new_songs["artist"][i]}', '{new_songs["artist_id"][i]}', '{new_songs["track"][i]}', '{new_songs["track_id"][i]}', {new_songs["duration"][i]}, '{new_songs["date_added"][i]}')""")
                except Exception as e:
                    print(e)
                    pass
        cur.close()

#remove songs from playlist table 
    def del_old_songs(self, playlist_id: str, track_id: str):
        with self.conn.cursor() as cur: 
            track_id_del = f"DELETE FROM spotify.playlist_{playlist_id} where track_id = '{track_id}'"
            try: 
                cur.execute(track_id_del)
            except Exception as e: 
                print(e)
                pass
        cur.close()

#gather playlist_DB 
    def get_playlist_df(self, playlist_id: str):
        snapshot = pd.DataFrame(self.conn.cursor().execute(f"SELECT * from spotify.playlist_{playlist_id} ORDER BY date_added ASC").fetchall(), columns=self.DB_cols)
        return snapshot