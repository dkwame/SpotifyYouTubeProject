import pandas as pd, os, sys, requests, json 
if os.getcwd() not in sys.path: 
    sys.path.insert(0, os.getcwd())
from Spotify import DB, SpotifyAPI
from YouTube import YouTubeAPI


#The primary objective of this program is to pull data from the Mystery Gang"s Spotify playlist
#sync the playlist with my Youtube playlist

#See below for an outline of this project
# 1. Refresh the authorization client credentials for this project (Both Spotify and YouTube)
# 2. Gather the last snapshot of tracks from our Spotify playlist database.
# 3. Compare our last snapshot with the tracks from our live Spotify playlist
# 4. Add missing tracks to our Spotify playlist database
# 5. Search tracks using the YouTube API
    # Select the most relevant search only if the runtime difference of no more than 20 seconds from the Spotify track
    # Gather the video id 
#6.  Use the video id to add song to playlist 

url = 'https://open.spotify.com/playlist/4BkimjsZvS8s45peOfA7bR'
playlist_id = SpotifyAPI().get_playlist_id(url)
response = SpotifyAPI().get_playlist_info(playlist_id)
playlist_name = response['name']
SpotifyAPI_df = SpotifyAPI().get_playlist_df(playlist_id)
SpotifyAPI_df
snapshot = DB().get_playlist_df(playlist_id)


try: 
    YouTubeAPI().refresh_token()
except:
    YouTubeAPI().grant_access()
    sys.exit() #once credits are assigned, the program is exited and the job will be ran again

#If new playlist is not in SpotifyDB then add to DB
##If new songs in Spotify API then add to Spotify DB
#Added some features in an attempt to make this program more portable for future use, for example the capability to add multiple playlists to the database. 
fresh_track_ids = []
if DB().conn.cursor().execute(f"SELECT * from spotify.playlist_ref where spot_playlist_id = '{playlist_id}'").fetchall() == []: 
    DB().create_playlist_table(playlist_id)
    DB().insert_new_songs(playlist_id, snapshot)
    DB().insert_playlist_ref(playlist_id, SpotifyAPI().get_playlist_info(playlist_id)['name'])
    DB().conn.close()
else: 
    for new_track_id in SpotifyAPI_df["track_id"]:
        if new_track_id not in snapshot["track_id"].values:
            print(new_track_id)
            fresh_track_ids.append(new_track_id)
    new_songs = SpotifyAPI_df[SpotifyAPI_df["track_id"].isin(fresh_track_ids)]
    new_songs = new_songs.reset_index(drop = True)
    DB().insert_new_songs(playlist_id, new_songs)

#If songs are removed from Spotify API then remove from YouTube playlist and Spotify DB
snapshot = DB().get_playlist_df(playlist_id)
removed_track_ids = []
for track_id in snapshot['track_id']:
    if track_id not in SpotifyAPI_df['track_id'].values:
        print(track_id)
        YouTubeAPI().remove_video(snapshot[snapshot['track_id']==track_id]['playlist_list_id'].values[0]) #remove from the YouTube playlist using the unique playlist_list_id
        DB().del_old_songs(playlist_id,track_id) #remove from the SpotifyDB using the unique track_id 

if len(DB().conn.cursor().execute(f"SELECT * from spotify.playlist_{playlist_id} where playlist_list_id is null").fetchall()) >= 1: 
    #for any observation where the video_id is null insert the video_id. A bit redundant
    snapshot = pd.read_sql(sql=f"SELECT * from spotify.playlist_{playlist_id} where playlist_list_id is null", con=DB().conn)
    snapshot = snapshot.fillna('')
    snapshot
    for i in range(len(snapshot)): 
        track = snapshot['track'][i]
        artist = snapshot['artist'][i]
        duration = snapshot['duration'][i]
        track_id = snapshot['track_id'][i]
        video_id = YouTubeAPI().search(track, artist, duration)
        print("Search passed")
        sql_statement = f"UPDATE spotify.playlist_{playlist_id} SET video_id = '{video_id}' where track_id = '{track_id}'"
        DB().conn.cursor().execute(sql_statement)
        DB().conn.close()
        try:
            response = YouTubeAPI().insert_video(video_id,YouTubeAPI().YT_playlist)
        except Exception as e:
            print(e)
            print(f"{track} by {artist} Errored out of the YouTube playlist insert method")
            pass
        if 'error' in response.keys():
            pass
            print(f"{track} by {artist} errored out on the YouTube playlist insert. Please review")
        else: 
            playlist_list_id = response['id']
            update_playlist_list_id = f"UPDATE spotify.playlist_4bkimjszvs8s45peofa7br SET playlist_list_id = '{playlist_list_id}' WHERE TRIM(video_id) = '{video_id}'"
            DB().conn.cursor().execute(update_playlist_list_id)
    DB().conn.close()
else: 
    sys.exit()
sys.exit()