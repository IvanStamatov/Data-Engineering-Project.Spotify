# Data-Engineering-Project.Spotify
A project about taking data from Spotify using their API and saving the data to a DB.

The logis of the program:
- Establish authentication for Spotify
    - This allows for automated generatioon of tokens for the Spotify API
- Check if an SQLite table exists and if not, create one
- Get the data from the Spotify API for recently played songs
- Check if the data already exists in the SQLite table and add it if it is new


To be implemented:
- Scheduled tasks with the schedule.py
- Visualization of the data


Tech stack used so far:
- Spotify's API
- SQLite
- DBeaver to view the SQLite data