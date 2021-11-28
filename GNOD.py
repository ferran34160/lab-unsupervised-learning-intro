import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler
from random import randint

with open("db_songs_clustered.txt", "rb") as f:   # Unpickling
    db_songs = pickle.load(f)
    
with open("top_songs.txt", "rb") as f:   # Unpickling
    top_songs = pickle.load(f)
    
model = pickle.load(open('model.p','rb'))
scaler = pickle.load(open('scaler.p','rb'))

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

secrets_file = open("secrets.txt","r")
string = secrets_file.read()
string.split('\n')
secrets_dict={}
for line in string.split('\n'):
    if len(line) > 0:
        secrets_dict[line.split(':')[0]]=line.split(':')[1]
        
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=secrets_dict['cid'],
                                                           client_secret=secrets_dict['csecret']))
                                                           

end = False
while (end == False):
    song = input("Enter your song: ")
    artist = input("Enter your artist: ")
    top100 = False
    for i in range(len(top_songs)):
        # if it's a Hot Song, then recommend another song from the list
        if ((top_songs['title'][i].lower() == song.lower()) & (top_songs['artist'][i].lower() == artist.lower())):
            rand_number = randint(0,len(top_songs))
            # printing recommendation:
            # print("I would recommend you to listen to: \"", top_songs['title'][rand_number], 
            # "\" by", top_songs['artist'][rand_number])
            print("This is a Hot Song!! I would recommend you to listen to: \"", top_songs['title'][rand_number], "\" by", top_songs['artist'][rand_number])
            top100 = True    
            end = True
            break
    # if is not a Hot song then predict one song in the same cluster
    if (top100 == False):
        results = sp.search(q=song, limit=50)
        if (results["tracks"]["items"] == []):
            print("There is no song with this name and artist in Spotify.")
            print("Please enter a new search.")
        else:
            for j in range(len(results["tracks"]["items"])):
                if ((results["tracks"]["items"][j]["artists"][0]["name"].lower()) == (artist.lower())):
                    uri = results["tracks"]["items"][j]["uri"]
                    # audio = pd.DataFrame(sp.audio_features(uri))[['danceability', 'energy', 'key', 'loudness', 
                    # 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
                    audio = pd.DataFrame(sp.audio_features(uri))[['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]

                    audio_scaled = scaler.transform(audio)
                    # this is the predicted cluster
                    pred_cluster = pd.Series(model.predict(audio_scaled),name='cluster')

                    # searching a random song in this cluster
                    songs_recom = db_songs[db_songs['cluster'] == pred_cluster[0]]
                    rand_number = randint(0,len(songs_recom))
                    recommended_song = songs_recom.loc[:,['title']].iloc[rand_number]
                    recommended_artist = songs_recom.loc[:,['artist']].iloc[rand_number]
                    print("Not a Hot Song :( But, we recommend you to listen to this song: \"", recommended_song.title,"\" by", recommended_artist.artist)
                    end = True
                    break
                                                         