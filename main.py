#The Great Library of Dependence
import requests
import json
from datetime import date
from datetime import datetime, timedelta
import sqlite3
import spotipy
import spotipy.util as util
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from wintoast import ToastNotifier

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"

# === Limitations
# Spotify stores 50 recent tracks information only.
# A track currently playing will not be visible in play history until it has completed. 
# A track must be played for more than 30 seconds to be included in play history

# Spotify tokens expire after an hour
os.environ['SPOTIPY_CLIENT_ID'] = ''
os.environ['SPOTIPY_CLIENT_SECRET'] = ''
os.environ['SPOTIPY_REDIRECT_URI'] = ''



def main():
    f = open("logs.txt", "a")
    f.write("[0] Script started at: " + datetime.now().strftime("%m-%d %H:%M:%S") + "\n")

    # Authorization Code Flow
    scope = 'user-read-recently-played'
    username = 'd3stamy'
    token = util.prompt_for_user_token(username,scope)

    # Headers based on the API's instructions
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=token)
    }
    f.write("[1] Token generated.\n")

    # Get the data from the API and store it
    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=40", headers = headers)

    data = r.json()
    f.write("[2] Data collected from Spotify API.\n")

    # Connect to an SQLite 
    conn = sqlite3.connect('myTracks.db')
    cursor = conn.cursor()

    # If the table does not exist, create a new one
    cursor.execute("""CREATE TABLE IF NOT EXISTS myTracks (
        song text,
        artist text,
        time real,
        date real
        )""")

    conn.commit()
    
    # Get a list of all timestamps currently in the SQLite 
    cursor.execute("SELECT time FROM myTracks")
    timestampList = cursor.fetchall()
    newTimeStampStr = ""
    for x in timestampList:
        newTimeStampStr += str(x)

    songsAdded = ""
    duplicateCount = 0
    songsAddedCount = 0

    for song in data["items"]:
        if str(song["played_at"]) in newTimeStampStr:
            # If the new timestamp is in the list of existing ones, do not add the data
            # print("Duplicate found: " + song["track"]["album"]["artists"][0]["name"] + " - "  + song["track"]["name"])
            duplicateCount += 1
        else:
            songName = song["track"]["name"]
            artistName = song["track"]["album"]["artists"][0]["name"]
            playedAt = song["played_at"]
            datePlayed = song["played_at"][0:10]
            cursor.execute('INSERT INTO myTracks VALUES (?,?,?,?)', (songName, artistName, playedAt, datePlayed))
            conn.commit()
            print("Added a new one: " + artistName + " - " + songName)
            songsAdded += artistName + " - " + songName + "\n"
            songsAddedCount += 1

    conn.close()
    f.write("[3] Data compared to existing in SQLite.\n")

    if not songsAdded:
        # print("There were no new songs.")
        f.write("[4] There were no new songs.\n")
    else:
        # print("songs added are: " + songsAdded)
        f.write("[4] There were [" + songsAddedCount + "] new songs\n")
        toaster = ToastNotifier()
        toaster.show_toast("New songs have been added.",
                       songsAdded,
                       icon_path="custom.ico",
                       duration=5)
    
    f.write("[5] Number of duplicates: " + str(duplicateCount) + "\n")

    f.write("[6] Script ended at  : " + datetime.now().strftime("%m-%d %H:%M:%S") + "\n======\n")
    f.close()
    return   


if __name__ == "__main__":
    main()



#scheduler = BlockingScheduler()
#scheduler.add_job(main, 'interval', minutes = 5)
#scheduler.start()