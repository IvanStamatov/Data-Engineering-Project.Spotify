import sqlalchemy
import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
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

print(token)






# Function for the validation process
def check_if_valid_data(df: pd.DataFrame) -> bool:
    # First is to check if the data frame is empty
    if df.empty:
        print("The data received is empty and no songs were downloaded.")
        return False
    # As our program extracts the songs listed to in the last 24 hours, it could be empty if you have not listened to any songs


    # Primary Key check
    # The primary key will be the time stamp as it is unique - you cant listen to two songs at the same time.
    # If there are two identical timestamps, this means that something has gone wrong
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key Check has been violated.")
        # If the check fails, it needs to shut down the pipeline so it doesnt not send incorrect data



    # Checking for any Nulls in the data received/downloaded
    if df.isnull().values.any():
        raise Exception("Null value found")
        # If a Null value comes in, terminate


    # Check that all timestamps are from yesterday's date as we want to save data that is only from the last 24 hours into our database
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    # The timestamp var does not have hours, minutes, seconds and microseconds - that's why we zero them here
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Comparing the yesterday var to the timestamp var
    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d') != yesterday:
            raise Exception("At least one of the returned songs does not have a yesterday's timestamp")
            # If there is a song with a timestamp outside of yesterday, the feed needs to fail
    return True



if __name__ == "__main__":

# ========== [ETL] Start of the Extract stage

    # Headers based on the API's instructions
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=token)
    }

    # Converting yesterday's date as it will be used daily   
    # We want to see the songs played for the last 24 hours
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1) #how many days back should the data date back to
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp), headers = headers)

    data = r.json()

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object      
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    # Prepare a dictionary in order to turn it into a pandas dataframe below       
    song_dict = {
        "song_name" : song_names,
        "artist_name": artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }


    song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
# ========== [ETL] End of the Extract stage



    # Calling the validation function
    if check_if_valid_data(song_df):
        print("Received data is valid. Proceeding to the next stage.")

    # print(song_df)
    


# ========== [ETL] Start of the Load stage
    # If the db does not exist, it will be created automatically
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)

    # Innitiate a connection to the new db
    conn= sqlite3.connect('my_played_tracks.sqlite')

    # A pointer that allows us to refer to specific rows in the db
    cursor = conn.cursor()


    # SQL to create a new table for our data
    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor.execute(sql_query)


    # Using pandas to insert data directly from a DataFrame into a DB
    try:
        song_df.to_sql('my_played_tracks', engine, index=False, if_exists='append')
        # The index is removed as we do not need the index panda gives
        # If the table exists, we want to append and not overwrite the table
    except:
        print("The data already exists in the database.")

    # Close the connection to the db
    conn.close()
    print("Entry in database was successfull.")

