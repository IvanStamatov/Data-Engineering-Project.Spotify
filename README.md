# Data-Engineering-Project.Spotify
A project about taking data from Spotify using their API and saving it into SQLite.

The logic of the program:
- Establish authentication for Spotify
    - This allows for automated generation of tokens for the Spotify API
- Check if an SQLite table exists and if not, create one
- Get the data from the Spotify API for recently played songs
- Check if the data already exists in the SQLite table and add it if it is new


To be implemented:
- Collecting additional data such as Genres, Album, etc.
- Visualization of the data

