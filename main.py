#The Great Library of Dependence
import pandas as pd 
import requests
import json
from datetime import date
from datetime import datetime, timedelta
import sqlite3
import spotipy
import spotipy.util as util
import os

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"

os.environ['SPOTIPY_CLIENT_ID'] = ''
os.environ['SPOTIPY_CLIENT_SECRET'] = ''
os.environ['SPOTIPY_REDIRECT_URI'] = ''

# Authorization Code Flow
scope = 'user-read-recently-played'
username = ''
token = util.prompt_for_user_token(username,scope)





if __name__ == "__main__":
    # Headers based on the API's instructions
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=token)
    }

# === Limitations
# Spotify stores 50 recent tracks information only.
# A track currently playing will not be visible in play history until it has completed. 
# A track must be played for more than 30 seconds to be included in play history.

    # Get the data from the API and store it
    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=40", headers = headers)

    data = r.json()

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []


    # Connect to an SQLite db
    conn = sqlite3.connect('myTracks.db')
    cursor = conn.cursor()
    print("Successfully Connected to SQLite")

    # If the table does not exist, create a new one
    cursor.execute("""CREATE TABLE IF NOT EXISTS myTracks (
        song text,
        artist text,
        time real,
        date real
        )""")

    conn.commit()

    # Get a list of all timestamps currently in the SQLite db
    cursor.execute("SELECT time FROM myTracks")
    timestampList = cursor.fetchall()
    newTimeStampStr = ""
    for x in timestampList:
        newTimeStampStr += str(x)


    for song in data["items"]:
        if str(song["played_at"]) in newTimeStampStr:
            # If the new timestamp is in the list of existing ones, do not add the data
            print("This song has already been added to the DB.")
        else:
            songName = song["track"]["name"]
            artistName = song["track"]["album"]["artists"][0]["name"]
            playedAt = song["played_at"]
            datePlayed = song["played_at"][0:10]
            cursor.execute('INSERT INTO myTracks VALUES (?,?,?,?)', (songName, artistName, playedAt, datePlayed))
            conn.commit()

    conn.close()
    print("End.")

