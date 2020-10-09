# Adding the Spotify Songs dataset to a database

This week, I'll be using the [Tidy Tuesday Spotify Songs dataset](https://github.com/rfordatascience/tidytuesday/blob/master/data/2020/2020-01-21/readme.md) to practice working with SQL a bit. If you're curious, the link to the dataset has more information on how this was gathered too. 

Let's start by getting the data and setting up. 

## 0. Data and setup


```python
# Packages needed 
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
```


```python
# Read in spotify dataset from github url
spotify_df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-01-21/spotify_songs.csv")
```

Let's also create a SQLite3 database on disk to use to store our data later. Note: if you don't have `sqlmagic`,  you may need to install it first as follows:


```python
! python3 -m pip install --quiet ipython-sql
```


```python
%load_ext sql
```

    The sql extension is already loaded. To reload it, use:
      %reload_ext sql


Then, you can make a new database (or connect to it, if it already exists): 


```python
%sql sqlite:///data/spotify.db
```

## 1. Normalize data to Third Normal Form 

Before we populate our database, it's good to normalize it; this enables us to remove redundancies and prevent inconsistencies later. 


### 1.1 Normalize data into First Normal Form 

First, let's get the data into First Normal Form (1NF). This means we want the data table (at least for now, let's consider this to be `spotify_df`) to have: 

1. A primary key (a unique, non-null column identifying each row). 
2. No repeating groups of columns
3. Each cell contains a single value

#### 1.1.1 Identify or create primary key

Let's start by looking at the columns available: 


```python
spotify_df.columns
```




    Index(['track_id', 'track_name', 'track_artist', 'track_popularity',
           'track_album_id', 'track_album_name', 'track_album_release_date',
           'playlist_name', 'playlist_id', 'playlist_genre', 'playlist_subgenre',
           'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
           'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
           'duration_ms'],
          dtype='object')



At first glance, it seems like `track_id` might be a good contender for a primary key, but let's confirm its values are unique and non-null for each row: 


```python
# Check if length of unique track_id values is equal to number of rows 
print("Is there a unique id per row?")
spotify_df.shape[0] == len(spotify_df["track_id"].unique())
```

    Is there a unique id per row?





    False



Hm, that doesn't seem to be the case. Let's look at one duplicated track_id to get a better sense for what a reasonable primary key could be: 


```python
# Get first track_id that's duplicated
first_duplicated_track_id = (spotify_df.
                             loc[spotify_df.duplicated(subset=['track_id'])]["track_id"].
                             iloc[0])

# Inspect rows of duplicated track_id
spotify_df.loc[spotify_df["track_id"] == first_duplicated_track_id].to_html()
```




    '<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n      <th></th>\n      <th>track_id</th>\n      <th>track_name</th>\n      <th>track_artist</th>\n      <th>track_popularity</th>\n      <th>track_album_id</th>\n      <th>track_album_name</th>\n      <th>track_album_release_date</th>\n      <th>playlist_name</th>\n      <th>playlist_id</th>\n      <th>playlist_genre</th>\n      <th>playlist_subgenre</th>\n      <th>danceability</th>\n      <th>energy</th>\n      <th>key</th>\n      <th>loudness</th>\n      <th>mode</th>\n      <th>speechiness</th>\n      <th>acousticness</th>\n      <th>instrumentalness</th>\n      <th>liveness</th>\n      <th>valence</th>\n      <th>tempo</th>\n      <th>duration_ms</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th>739</th>\n      <td>1HfMVBKM75vxSfsQ5VefZ5</td>\n      <td>Lose You To Love Me</td>\n      <td>Selena Gomez</td>\n      <td>93</td>\n      <td>3tBkjgxDqAwss76O1YHsSY</td>\n      <td>Lose You To Love Me</td>\n      <td>2019-10-23</td>\n      <td>Todo Éxitos</td>\n      <td>2ji5tRQVfnhaX1w9FhmSzk</td>\n      <td>pop</td>\n      <td>dance pop</td>\n      <td>0.505</td>\n      <td>0.34</td>\n      <td>4</td>\n      <td>-9.005</td>\n      <td>1</td>\n      <td>0.0438</td>\n      <td>0.576</td>\n      <td>0.0</td>\n      <td>0.21</td>\n      <td>0.0916</td>\n      <td>101.993</td>\n      <td>206459</td>\n    </tr>\n    <tr>\n      <th>1299</th>\n      <td>1HfMVBKM75vxSfsQ5VefZ5</td>\n      <td>Lose You To Love Me</td>\n      <td>Selena Gomez</td>\n      <td>93</td>\n      <td>3tBkjgxDqAwss76O1YHsSY</td>\n      <td>Lose You To Love Me</td>\n      <td>2019-10-23</td>\n      <td>Pop - Pop UK - 2019 - Canadian Pop - 2019 - Pop</td>\n      <td>46Cl6dmeiylK6TRGXr7hHe</td>\n      <td>pop</td>\n      <td>post-teen pop</td>\n      <td>0.505</td>\n      <td>0.34</td>\n      <td>4</td>\n      <td>-9.005</td>\n      <td>1</td>\n      <td>0.0438</td>\n      <td>0.576</td>\n      <td>0.0</td>\n      <td>0.21</td>\n      <td>0.0916</td>\n      <td>101.993</td>\n      <td>206459</td>\n    </tr>\n    <tr>\n      <th>18320</th>\n      <td>1HfMVBKM75vxSfsQ5VefZ5</td>\n      <td>Lose You To Love Me</td>\n      <td>Selena Gomez</td>\n      <td>93</td>\n      <td>3tBkjgxDqAwss76O1YHsSY</td>\n      <td>Lose You To Love Me</td>\n      <td>2019-10-23</td>\n      <td>2020 Hits &amp; 2019  Hits – Top Global Tracks 🔥🔥🔥</td>\n      <td>4JkkvMpVl4lSioqQjeAL0q</td>\n      <td>latin</td>\n      <td>latin pop</td>\n      <td>0.505</td>\n      <td>0.34</td>\n      <td>4</td>\n      <td>-9.005</td>\n      <td>1</td>\n      <td>0.0438</td>\n      <td>0.576</td>\n      <td>0.0</td>\n      <td>0.21</td>\n      <td>0.0916</td>\n      <td>101.993</td>\n      <td>206459</td>\n    </tr>\n    <tr>\n      <th>19730</th>\n      <td>1HfMVBKM75vxSfsQ5VefZ5</td>\n      <td>Lose You To Love Me</td>\n      <td>Selena Gomez</td>\n      <td>93</td>\n      <td>3tBkjgxDqAwss76O1YHsSY</td>\n      <td>Lose You To Love Me</td>\n      <td>2019-10-23</td>\n      <td>2020 Hits &amp; 2019  Hits – Top Global Tracks 🔥🔥🔥</td>\n      <td>4JkkvMpVl4lSioqQjeAL0q</td>\n      <td>latin</td>\n      <td>latin hip hop</td>\n      <td>0.505</td>\n      <td>0.34</td>\n      <td>4</td>\n      <td>-9.005</td>\n      <td>1</td>\n      <td>0.0438</td>\n      <td>0.576</td>\n      <td>0.0</td>\n      <td>0.21</td>\n      <td>0.0916</td>\n      <td>101.993</td>\n      <td>206459</td>\n    </tr>\n    <tr>\n      <th>21555</th>\n      <td>1HfMVBKM75vxSfsQ5VefZ5</td>\n      <td>Lose You To Love Me</td>\n      <td>Selena Gomez</td>\n      <td>93</td>\n      <td>3tBkjgxDqAwss76O1YHsSY</td>\n      <td>Lose You To Love Me</td>\n      <td>2019-10-23</td>\n      <td>Most Popular 2020 TOP 50</td>\n      <td>1fqkbjEACMlekdddm5aobE</td>\n      <td>r&amp;b</td>\n      <td>urban contemporary</td>\n      <td>0.505</td>\n      <td>0.34</td>\n      <td>4</td>\n      <td>-9.005</td>\n      <td>1</td>\n      <td>0.0438</td>\n      <td>0.576</td>\n      <td>0.0</td>\n      <td>0.21</td>\n      <td>0.0916</td>\n      <td>101.993</td>\n      <td>206459</td>\n    </tr>\n    <tr>\n      <th>23641</th>\n      <td>1HfMVBKM75vxSfsQ5VefZ5</td>\n      <td>Lose You To Love Me</td>\n      <td>Selena Gomez</td>\n      <td>93</td>\n      <td>3tBkjgxDqAwss76O1YHsSY</td>\n      <td>Lose You To Love Me</td>\n      <td>2019-10-23</td>\n      <td>Latest Hits 2020 - Pop, Hip Hop &amp; RnB</td>\n      <td>7FqZlaYKkQmVnguJbHuj2a</td>\n      <td>r&amp;b</td>\n      <td>hip pop</td>\n      <td>0.505</td>\n      <td>0.34</td>\n      <td>4</td>\n      <td>-9.005</td>\n      <td>1</td>\n      <td>0.0438</td>\n      <td>0.576</td>\n      <td>0.0</td>\n      <td>0.21</td>\n      <td>0.0916</td>\n      <td>101.993</td>\n      <td>206459</td>\n    </tr>\n    <tr>\n      <th>30388</th>\n      <td>1HfMVBKM75vxSfsQ5VefZ5</td>\n      <td>Lose You To Love Me</td>\n      <td>Selena Gomez</td>\n      <td>93</td>\n      <td>3tBkjgxDqAwss76O1YHsSY</td>\n      <td>Lose You To Love Me</td>\n      <td>2019-10-23</td>\n      <td>2010 - 2011 - 2012 - 2013 - 2014 - 2015 - 2016 - 2017 - 2018 - 2019 - 2020 TOP HITS</td>\n      <td>2DjIfVDXGYDgRxw7IJTKVb</td>\n      <td>edm</td>\n      <td>pop edm</td>\n      <td>0.505</td>\n      <td>0.34</td>\n      <td>4</td>\n      <td>-9.005</td>\n      <td>1</td>\n      <td>0.0438</td>\n      <td>0.576</td>\n      <td>0.0</td>\n      <td>0.21</td>\n      <td>0.0916</td>\n      <td>101.993</td>\n      <td>206459</td>\n    </tr>\n  </tbody>\n</table>'




```python

```

Ok-- it seems like the `track_id` is redundant here because it's on multiple playlists. We could combine the `track_id` with `playlist_id` to create a unique ID per row, but considering that they have to do with different things it probably makes more sense to just split the data frame into **two** tables (track and playlist) and allocate relevant columns accordingly. So, let's do that: 


```python
spotify_df.columns
```




    Index(['track_id', 'track_name', 'track_artist', 'track_popularity',
           'track_album_id', 'track_album_name', 'track_album_release_date',
           'playlist_name', 'playlist_id', 'playlist_genre', 'playlist_subgenre',
           'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
           'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
           'duration_ms'],
          dtype='object')




```python
# columns relevant to track
track_columns = ['track_id', 
                 'track_name', 
                 'track_artist', 
                 'track_popularity',
                 'track_album_id', 
                 'track_album_name', 
                 'track_album_release_date',
                 'danceability', 
                 'energy', 
                 'key', 
                 'loudness', 
                 'mode', 
                 'speechiness',
                 'acousticness', 
                 'instrumentalness', 
                 'liveness', 
                 'valence', 
                 'tempo',
                 'duration_ms'] 

# columns relevant to playlist 
playlist_columns = ['playlist_id',
                    'playlist_name', 
                    'playlist_genre', 
                    'playlist_subgenre']

# Create a dictionary of 2 dataframes (track_df and playlist_df)
spotify_df_dict = {'track' : spotify_df.loc[:,track_columns].drop_duplicates(),
                  'playlist' : spotify_df.loc[:,playlist_columns].drop_duplicates()}
```

Now let's confirm that `track_id` and `playlist_id` are unique and non-null within each DataFrame: 


```python
# Check track_id is unique per row in track df
print("TRACK:")
print("Is there a unique id per row?")
print(spotify_df_dict["track"].shape[0] == len(spotify_df_dict["track"]["track_id"].unique()))

# Check track_id has no NA values
print("Are there NA values?")
print(spotify_df_dict["track"]["track_id"].isnull().any())

# Check playlist_id is unique per row in playlist df
print("\nPLAYLIST:")
print("Is there a unique id per row?")
print(spotify_df_dict["playlist"].shape[0] == len(spotify_df_dict["playlist"]["playlist_id"].unique()))

# Check playlist_id has no NA values
print("Are there NA values?")
print(spotify_df_dict["playlist"]["playlist_id"].isnull().any())
```

    TRACK:
    Is there a unique id per row?
    True
    Are there NA values?
    False
    
    PLAYLIST:
    Is there a unique id per row?
    False
    Are there NA values?
    False


Seems like `playlist_id` still isn't unique. Let's look more closely at the rows where `playlist_id` is duplicated: 


```python
duplicated_playlist_ids = (spotify_df_dict["playlist"].
 loc[spotify_df_dict["playlist"].duplicated(subset=['playlist_id'])]["playlist_id"])

spotify_df_dict["playlist"][spotify_df_dict["playlist"]["playlist_id"].
                            isin(duplicated_playlist_ids)].sort_values(by=["playlist_id"])
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>playlist_id</th>
      <th>playlist_name</th>
      <th>playlist_genre</th>
      <th>playlist_subgenre</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>29945</th>
      <td>25ButZrVb1Zj1MJioMs09D</td>
      <td>EDM 2020 House &amp; Dance</td>
      <td>edm</td>
      <td>pop edm</td>
    </tr>
    <tr>
      <th>27216</th>
      <td>25ButZrVb1Zj1MJioMs09D</td>
      <td>EDM 2020 House &amp; Dance</td>
      <td>edm</td>
      <td>electro house</td>
    </tr>
    <tr>
      <th>30804</th>
      <td>2CJsD3fcYJWcliEKnwmovU</td>
      <td>TOP 50 GLOBAL 2020 UPDATED WEEKLY 🌍🎶 WORLDWIDE</td>
      <td>edm</td>
      <td>pop edm</td>
    </tr>
    <tr>
      <th>23436</th>
      <td>2CJsD3fcYJWcliEKnwmovU</td>
      <td>TOP 50 GLOBAL 2020 UPDATED WEEKLY 🌍🎶 WORLDWIDE</td>
      <td>r&amp;b</td>
      <td>hip pop</td>
    </tr>
    <tr>
      <th>1067</th>
      <td>37i9dQZF1DWTHM4kX49UKs</td>
      <td>Ultimate Indie Presents... Best Indie Tracks o...</td>
      <td>pop</td>
      <td>dance pop</td>
    </tr>
    <tr>
      <th>22829</th>
      <td>37i9dQZF1DWTHM4kX49UKs</td>
      <td>Ultimate Indie Presents... Best Indie Tracks o...</td>
      <td>r&amp;b</td>
      <td>hip pop</td>
    </tr>
    <tr>
      <th>10387</th>
      <td>37i9dQZF1DX4OjfOteYnH8</td>
      <td>Flow Selecto</td>
      <td>rap</td>
      <td>trap</td>
    </tr>
    <tr>
      <th>19687</th>
      <td>37i9dQZF1DX4OjfOteYnH8</td>
      <td>Flow Selecto</td>
      <td>latin</td>
      <td>reggaeton</td>
    </tr>
    <tr>
      <th>12900</th>
      <td>3Ho3iO0iJykgEQNbjB2sic</td>
      <td>Classic Rock 70s 80s 90s, Rock Classics - 70s ...</td>
      <td>rock</td>
      <td>classic rock</td>
    </tr>
    <tr>
      <th>15155</th>
      <td>3Ho3iO0iJykgEQNbjB2sic</td>
      <td>Classic Rock 70s 80s 90s, Rock Classics - 70s ...</td>
      <td>rock</td>
      <td>hard rock</td>
    </tr>
    <tr>
      <th>30196</th>
      <td>3xMQTDLOIGvj3lWH5e5x6F</td>
      <td>Charts 2020 🔥Top 2020🔥Hits 2020🔥Summer 2020🔥Po...</td>
      <td>edm</td>
      <td>pop edm</td>
    </tr>
    <tr>
      <th>23099</th>
      <td>3xMQTDLOIGvj3lWH5e5x6F</td>
      <td>Charts 2020 🔥Top 2020🔥Hits 2020🔥Summer 2020🔥Po...</td>
      <td>r&amp;b</td>
      <td>hip pop</td>
    </tr>
    <tr>
      <th>19703</th>
      <td>4JkkvMpVl4lSioqQjeAL0q</td>
      <td>2020 Hits &amp; 2019  Hits – Top Global Tracks 🔥🔥🔥</td>
      <td>latin</td>
      <td>latin hip hop</td>
    </tr>
    <tr>
      <th>18295</th>
      <td>4JkkvMpVl4lSioqQjeAL0q</td>
      <td>2020 Hits &amp; 2019  Hits – Top Global Tracks 🔥🔥🔥</td>
      <td>latin</td>
      <td>latin pop</td>
    </tr>
    <tr>
      <th>23755</th>
      <td>4JkkvMpVl4lSioqQjeAL0q</td>
      <td>2020 Hits &amp; 2019  Hits – Top Global Tracks 🔥🔥🔥</td>
      <td>r&amp;b</td>
      <td>hip pop</td>
    </tr>
    <tr>
      <th>27962</th>
      <td>6KnQDwp0syvhfHOR4lWP7x</td>
      <td>Fitness Workout Electro | House | Dance | Prog...</td>
      <td>edm</td>
      <td>electro house</td>
    </tr>
    <tr>
      <th>31024</th>
      <td>6KnQDwp0syvhfHOR4lWP7x</td>
      <td>Fitness Workout Electro | House | Dance | Prog...</td>
      <td>edm</td>
      <td>progressive electro house</td>
    </tr>
  </tbody>
</table>
</div>



The issue seems to be that some playlists are listed under two subgenres. We want to keep a single value per column so combining the redundant subgenres isn't a good idea. So, let's instead just create a new unique id for the playlist dataframe:


```python
spotify_df_dict["playlist"]["playlist_uid"] = list(range(0, spotify_df_dict["playlist"].shape[0]))
```


```python
# Check playlist_uid is unique per row in playlist df
print("Is there a unique id per row?")
print(spotify_df_dict["playlist"].shape[0] == len(spotify_df_dict["playlist"]["playlist_uid"].unique()))

# Check playlist_uid has no NA values
print("Are there NA values?")
print(spotify_df_dict["playlist"]["playlist_uid"].isnull().any())
```

    Is there a unique id per row?
    True
    Are there NA values?
    False


Great! Moving on. 

#### 1.1.2 Check that there are no repeating columns 

For the track DataFrame, none of the columns seem to repeat: 


```python
spotify_df_dict["track"].head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>track_id</th>
      <th>track_name</th>
      <th>track_artist</th>
      <th>track_popularity</th>
      <th>track_album_id</th>
      <th>track_album_name</th>
      <th>track_album_release_date</th>
      <th>danceability</th>
      <th>energy</th>
      <th>key</th>
      <th>loudness</th>
      <th>mode</th>
      <th>speechiness</th>
      <th>acousticness</th>
      <th>instrumentalness</th>
      <th>liveness</th>
      <th>valence</th>
      <th>tempo</th>
      <th>duration_ms</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>6f807x0ima9a1j3VPbc7VN</td>
      <td>I Don't Care (with Justin Bieber) - Loud Luxur...</td>
      <td>Ed Sheeran</td>
      <td>66</td>
      <td>2oCs0DGTsRO98Gh5ZSl2Cx</td>
      <td>I Don't Care (with Justin Bieber) [Loud Luxury...</td>
      <td>2019-06-14</td>
      <td>0.748</td>
      <td>0.916</td>
      <td>6</td>
      <td>-2.634</td>
      <td>1</td>
      <td>0.0583</td>
      <td>0.1020</td>
      <td>0.000000</td>
      <td>0.0653</td>
      <td>0.518</td>
      <td>122.036</td>
      <td>194754</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0r7CVbZTWZgbTCYdfa2P31</td>
      <td>Memories - Dillon Francis Remix</td>
      <td>Maroon 5</td>
      <td>67</td>
      <td>63rPSO264uRjW1X5E6cWv6</td>
      <td>Memories (Dillon Francis Remix)</td>
      <td>2019-12-13</td>
      <td>0.726</td>
      <td>0.815</td>
      <td>11</td>
      <td>-4.969</td>
      <td>1</td>
      <td>0.0373</td>
      <td>0.0724</td>
      <td>0.004210</td>
      <td>0.3570</td>
      <td>0.693</td>
      <td>99.972</td>
      <td>162600</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1z1Hg7Vb0AhHDiEmnDE79l</td>
      <td>All the Time - Don Diablo Remix</td>
      <td>Zara Larsson</td>
      <td>70</td>
      <td>1HoSmj2eLcsrR0vE9gThr4</td>
      <td>All the Time (Don Diablo Remix)</td>
      <td>2019-07-05</td>
      <td>0.675</td>
      <td>0.931</td>
      <td>1</td>
      <td>-3.432</td>
      <td>0</td>
      <td>0.0742</td>
      <td>0.0794</td>
      <td>0.000023</td>
      <td>0.1100</td>
      <td>0.613</td>
      <td>124.008</td>
      <td>176616</td>
    </tr>
    <tr>
      <th>3</th>
      <td>75FpbthrwQmzHlBJLuGdC7</td>
      <td>Call You Mine - Keanu Silva Remix</td>
      <td>The Chainsmokers</td>
      <td>60</td>
      <td>1nqYsOef1yKKuGOVchbsk6</td>
      <td>Call You Mine - The Remixes</td>
      <td>2019-07-19</td>
      <td>0.718</td>
      <td>0.930</td>
      <td>7</td>
      <td>-3.778</td>
      <td>1</td>
      <td>0.1020</td>
      <td>0.0287</td>
      <td>0.000009</td>
      <td>0.2040</td>
      <td>0.277</td>
      <td>121.956</td>
      <td>169093</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1e8PAfcKUYoKkxPhrHqw4x</td>
      <td>Someone You Loved - Future Humans Remix</td>
      <td>Lewis Capaldi</td>
      <td>69</td>
      <td>7m7vv9wlQ4i0LFuJiE2zsQ</td>
      <td>Someone You Loved (Future Humans Remix)</td>
      <td>2019-03-05</td>
      <td>0.650</td>
      <td>0.833</td>
      <td>1</td>
      <td>-4.672</td>
      <td>1</td>
      <td>0.0359</td>
      <td>0.0803</td>
      <td>0.000000</td>
      <td>0.0833</td>
      <td>0.725</td>
      <td>123.976</td>
      <td>189052</td>
    </tr>
  </tbody>
</table>
</div>



For the playlist DataFrame (since we added a unique identifying column), there are no repeating groups of columns:


```python
spotify_df_dict["playlist"].head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>playlist_id</th>
      <th>playlist_name</th>
      <th>playlist_genre</th>
      <th>playlist_subgenre</th>
      <th>playlist_uid</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>Pop Remix</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>0</td>
    </tr>
    <tr>
      <th>70</th>
      <td>37i9dQZF1DWZQaaqNMbbXa</td>
      <td>Dance Pop</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>1</td>
    </tr>
    <tr>
      <th>167</th>
      <td>37i9dQZF1DX2ENAPP1Tyed</td>
      <td>Dance Room</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>2</td>
    </tr>
    <tr>
      <th>223</th>
      <td>37i9dQZF1DWSJHnPb1f0X3</td>
      <td>Cardio</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>3</td>
    </tr>
    <tr>
      <th>272</th>
      <td>37i9dQZF1DX6pH08wMhkaI</td>
      <td>Dance Pop Hits</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



#### 1.1.3 Each cell contains a single value

From our inspection of the DataFrames in 1.2, we see that each cell contains a single value; so, this requirement is satisfied.  

### 2. Normalize data into Second Normal Form 

Now we're ready to get our data into Second Normal form ("2NF"). This means we want each table to have all columns in each row to depend fully on candidate keys. Basically, we'll ask if each column in the two tables we have so far serve to describe what the primary key identifies. 

#### 2.1 Playlist table 

The columns of the playlist table are as follows: 


```python
spotify_df_dict["playlist"].columns
```




    Index(['playlist_id', 'playlist_name', 'playlist_genre', 'playlist_subgenre',
           'playlist_uid'],
          dtype='object')



Each column describes what the primary key identifies (a playlist), so 2NF is satisfied for this table. 

#### 2.2. Track table

The columns of the track table are as follows: 


```python
spotify_df_dict["track"].columns
```




    Index(['track_id', 'track_name', 'track_artist', 'track_popularity',
           'track_album_id', 'track_album_name', 'track_album_release_date',
           'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
           'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
           'duration_ms'],
          dtype='object')



Here, we notice that some of the columns (specifically, `track_album_id`, `track_album_name`, `track_album_release_date`) relate to the **album** of the track, not the track itself (as the other columns do). So, let's move the album-related columns to their own table: 


```python
album_columns = ["track_album_id",
                "track_album_name",
                "track_album_release_date"]

# Create new DataFrame of album information, dropping duplicates
spotify_df_dict["album"] = spotify_df_dict["track"][album_columns].drop_duplicates()

# Check that track_album_id is an appropriate primary key
print("Is there a unique id per row?")
print(spotify_df_dict["album"].shape[0] == len(spotify_df_dict["album"]["track_album_id"].unique()))

# Check playlist_uid has no NA values
print("Are there NA values?")
print(spotify_df_dict["album"]["track_album_id"].isnull().any())
```

    Is there a unique id per row?
    True
    Are there NA values?
    False


Great! Now let's remove those columns from the track DataFrame and we should be all set with 2NF: 


```python
spotify_df_dict["track"].drop(album_columns, axis=1, inplace=True)

# Confirm that album columns were removed
spotify_df_dict["track"].columns
```




    Index(['track_id', 'track_name', 'track_artist', 'track_popularity',
           'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
           'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
           'duration_ms'],
          dtype='object')



### 3. Normalize data into Third Normal Form (3NF)

Lastly, we want to confirm that there are no transitive dependencies between non-candidate columns. 

#### 3.1 Album table

Let's look at the columns again: 


```python
spotify_df_dict["album"].head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>track_album_id</th>
      <th>track_album_name</th>
      <th>track_album_release_date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2oCs0DGTsRO98Gh5ZSl2Cx</td>
      <td>I Don't Care (with Justin Bieber) [Loud Luxury...</td>
      <td>2019-06-14</td>
    </tr>
    <tr>
      <th>1</th>
      <td>63rPSO264uRjW1X5E6cWv6</td>
      <td>Memories (Dillon Francis Remix)</td>
      <td>2019-12-13</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1HoSmj2eLcsrR0vE9gThr4</td>
      <td>All the Time (Don Diablo Remix)</td>
      <td>2019-07-05</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1nqYsOef1yKKuGOVchbsk6</td>
      <td>Call You Mine - The Remixes</td>
      <td>2019-07-19</td>
    </tr>
    <tr>
      <th>4</th>
      <td>7m7vv9wlQ4i0LFuJiE2zsQ</td>
      <td>Someone You Loved (Future Humans Remix)</td>
      <td>2019-03-05</td>
    </tr>
  </tbody>
</table>
</div>



Each column depends on the album_id (or row number), so there are no 3NF violations. 

#### 3.2 Playlist table 


```python
spotify_df_dict["playlist"].head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>playlist_id</th>
      <th>playlist_name</th>
      <th>playlist_genre</th>
      <th>playlist_subgenre</th>
      <th>playlist_uid</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>Pop Remix</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>0</td>
    </tr>
    <tr>
      <th>70</th>
      <td>37i9dQZF1DWZQaaqNMbbXa</td>
      <td>Dance Pop</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>1</td>
    </tr>
    <tr>
      <th>167</th>
      <td>37i9dQZF1DX2ENAPP1Tyed</td>
      <td>Dance Room</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>2</td>
    </tr>
    <tr>
      <th>223</th>
      <td>37i9dQZF1DWSJHnPb1f0X3</td>
      <td>Cardio</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>3</td>
    </tr>
    <tr>
      <th>272</th>
      <td>37i9dQZF1DX6pH08wMhkaI</td>
      <td>Dance Pop Hits</td>
      <td>pop</td>
      <td>dance pop</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



Here, `playlist_subgenre` violates 3NF, because it only depends on the `playlist_uid` via the `playlist_genre`. So, let's split that out (with `playlist_genre`) into a separate genre table: 


```python
genre_columns = ["playlist_genre",
                "playlist_subgenre"]

# Create new DataFrame of genre information, dropping duplicates
spotify_df_dict["genre"] = spotify_df_dict["playlist"][genre_columns].drop_duplicates()

# Check that playlist_subgenre is an appropriate primary key
print("Is there a unique id per row?")
print(spotify_df_dict["genre"].shape[0] == len(spotify_df_dict["genre"]["playlist_subgenre"].unique()))

# Check playlist_uid has no NA values
print("Are there NA values?")
print(spotify_df_dict["genre"]["playlist_subgenre"].isnull().any())
```

    Is there a unique id per row?
    True
    Are there NA values?
    False


Great. Lastly, let's remove `playlist_genre` and `playlist_subgenre` from the playlist table: 


```python
spotify_df_dict["playlist"].drop(["playlist_genre","playlist_subgenre"], axis=1, inplace=True)

# Confirm that album columns were removed
spotify_df_dict["playlist"].columns
```




    Index(['playlist_id', 'playlist_name', 'playlist_uid'], dtype='object')



#### 3.3 Track table


```python
spotify_df_dict["track"].head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>track_id</th>
      <th>track_name</th>
      <th>track_artist</th>
      <th>track_popularity</th>
      <th>danceability</th>
      <th>energy</th>
      <th>key</th>
      <th>loudness</th>
      <th>mode</th>
      <th>speechiness</th>
      <th>acousticness</th>
      <th>instrumentalness</th>
      <th>liveness</th>
      <th>valence</th>
      <th>tempo</th>
      <th>duration_ms</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>6f807x0ima9a1j3VPbc7VN</td>
      <td>I Don't Care (with Justin Bieber) - Loud Luxur...</td>
      <td>Ed Sheeran</td>
      <td>66</td>
      <td>0.748</td>
      <td>0.916</td>
      <td>6</td>
      <td>-2.634</td>
      <td>1</td>
      <td>0.0583</td>
      <td>0.1020</td>
      <td>0.000000</td>
      <td>0.0653</td>
      <td>0.518</td>
      <td>122.036</td>
      <td>194754</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0r7CVbZTWZgbTCYdfa2P31</td>
      <td>Memories - Dillon Francis Remix</td>
      <td>Maroon 5</td>
      <td>67</td>
      <td>0.726</td>
      <td>0.815</td>
      <td>11</td>
      <td>-4.969</td>
      <td>1</td>
      <td>0.0373</td>
      <td>0.0724</td>
      <td>0.004210</td>
      <td>0.3570</td>
      <td>0.693</td>
      <td>99.972</td>
      <td>162600</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1z1Hg7Vb0AhHDiEmnDE79l</td>
      <td>All the Time - Don Diablo Remix</td>
      <td>Zara Larsson</td>
      <td>70</td>
      <td>0.675</td>
      <td>0.931</td>
      <td>1</td>
      <td>-3.432</td>
      <td>0</td>
      <td>0.0742</td>
      <td>0.0794</td>
      <td>0.000023</td>
      <td>0.1100</td>
      <td>0.613</td>
      <td>124.008</td>
      <td>176616</td>
    </tr>
    <tr>
      <th>3</th>
      <td>75FpbthrwQmzHlBJLuGdC7</td>
      <td>Call You Mine - Keanu Silva Remix</td>
      <td>The Chainsmokers</td>
      <td>60</td>
      <td>0.718</td>
      <td>0.930</td>
      <td>7</td>
      <td>-3.778</td>
      <td>1</td>
      <td>0.1020</td>
      <td>0.0287</td>
      <td>0.000009</td>
      <td>0.2040</td>
      <td>0.277</td>
      <td>121.956</td>
      <td>169093</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1e8PAfcKUYoKkxPhrHqw4x</td>
      <td>Someone You Loved - Future Humans Remix</td>
      <td>Lewis Capaldi</td>
      <td>69</td>
      <td>0.650</td>
      <td>0.833</td>
      <td>1</td>
      <td>-4.672</td>
      <td>1</td>
      <td>0.0359</td>
      <td>0.0803</td>
      <td>0.000000</td>
      <td>0.0833</td>
      <td>0.725</td>
      <td>123.976</td>
      <td>189052</td>
    </tr>
  </tbody>
</table>
</div>



Each column depends on the track_id (or row number), so there are no 3NF violations. 

### 3. Populate tables of SQLite3 database

Now we're (almost) ready to populate our database! But first, we need to resolve an issue-- our tables are no longer linked! We need to add **foreign keys** (or, a field/column linking a given table to the primary key of a second table) because this enable us to maintain the relationships between the tables. 

#### 3.1 Add foreign keys to DataFrames 

We start by using the original DataFrame to make a map between each of the primary keys: `track_id`, `playlist_id` (* we will map to `playlist_uid` in a second), `playlist_subgenre`, and `track_album_id`):


```python
original_id_columns = ["track_id",
                      "playlist_id",
                      "playlist_subgenre",
                      "track_album_id"]
id_map_df = spotify_df[original_id_columns].drop_duplicates()
id_map_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>track_id</th>
      <th>playlist_id</th>
      <th>playlist_subgenre</th>
      <th>track_album_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>6f807x0ima9a1j3VPbc7VN</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>2oCs0DGTsRO98Gh5ZSl2Cx</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0r7CVbZTWZgbTCYdfa2P31</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>63rPSO264uRjW1X5E6cWv6</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1z1Hg7Vb0AhHDiEmnDE79l</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>1HoSmj2eLcsrR0vE9gThr4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>75FpbthrwQmzHlBJLuGdC7</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>1nqYsOef1yKKuGOVchbsk6</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1e8PAfcKUYoKkxPhrHqw4x</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>7m7vv9wlQ4i0LFuJiE2zsQ</td>
    </tr>
  </tbody>
</table>
</div>



Now we add `playlist_uid` to make this a complete map: 


```python
id_map_df = id_map_df.merge(spotify_df_dict["playlist"].loc[:,["playlist_id", "playlist_uid"]],
                           how="left",
                           on="playlist_id")
id_map_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>track_id</th>
      <th>playlist_id</th>
      <th>playlist_subgenre</th>
      <th>track_album_id</th>
      <th>playlist_uid</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>6f807x0ima9a1j3VPbc7VN</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>2oCs0DGTsRO98Gh5ZSl2Cx</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0r7CVbZTWZgbTCYdfa2P31</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>63rPSO264uRjW1X5E6cWv6</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1z1Hg7Vb0AhHDiEmnDE79l</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>1HoSmj2eLcsrR0vE9gThr4</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>75FpbthrwQmzHlBJLuGdC7</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>1nqYsOef1yKKuGOVchbsk6</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1e8PAfcKUYoKkxPhrHqw4x</td>
      <td>37i9dQZF1DXcZDD7cfEKhW</td>
      <td>dance pop</td>
      <td>7m7vv9wlQ4i0LFuJiE2zsQ</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



And now we add the relevant foreign keys to preserve the DataFrame's original links via joins:  


```python
# Add participant_uid and album_id foreign keys to track df 
spotify_df_dict["track"] = (spotify_df_dict["track"].
                            merge(id_map_df.loc[:,["track_id","playlist_uid", "track_album_id"]],
                                 how="left",
                                 on="track_id"))

# Add playlist_subgenre foreign keys to playlist df
spotify_df_dict["playlist"] = (spotify_df_dict["playlist"].
                            merge(id_map_df.loc[:,["playlist_uid", "playlist_subgenre"]],
                                 how="left",
                                 on="playlist_uid"))
```

Ok, now we can finally...

#### 3.2 Populate tables of database

First, let's create an engine to the database we previously defined:


```python
engine = create_engine('sqlite:///data/spotify.db')
```

And then we write each value of our dictionary of DataFrames to a table (pandas makes this really easy):


```python
for key in spotify_df_dict.keys():
    spotify_df_dict[key].to_sql(key, con=engine)
```

### 4. Sample SQL query: Find the names of all playlists that contain instrumentals

Lastly, let's perform a sample query on our database. We see from [the dataset documentation](https://github.com/rfordatascience/tidytuesday/blob/master/data/2020/2020-01-21/readme.md) that the `instrumentalness` column (which is in the `track` table) assigns a value between 0 and 1 to each track, where values above 0.5 indicate the track has likely instrumental content. 

So, we want to: 

1. Identify which distinct `playlist_uid`s have `instrumentalness` > 0.5 in the track table.  
2. See which `playlist_name`s these `playlist_uids` belong to. 

We'll do this with a sub-query, as follows: 


```python
%%sql 

SELECT DISTINCT playlist_name FROM playlist
WHERE playlist_uid IN (
    SELECT playlist_uid FROM track
    WHERE instrumentalness > 0.5
)
```

     * sqlite:///data/spotify.db
    Done.





<table>
    <tr>
        <th>playlist_name</th>
    </tr>
    <tr>
        <td>Pop Remix</td>
    </tr>
    <tr>
        <td>Dance Room</td>
    </tr>
    <tr>
        <td>Pop Warmup 130 BPM</td>
    </tr>
    <tr>
        <td>Dance Pop</td>
    </tr>
    <tr>
        <td>Dance Pop Tunes</td>
    </tr>
    <tr>
        <td>Pop / Dance</td>
    </tr>
    <tr>
        <td>Todo Éxitos</td>
    </tr>
    <tr>
        <td>90s Dance Hits</td>
    </tr>
    <tr>
        <td>Christian Dance Party</td>
    </tr>
    <tr>
        <td>Pop Dance Hits</td>
    </tr>
    <tr>
        <td>Ultimate Indie Presents... Best Indie Tracks of the 2010s</td>
    </tr>
    <tr>
        <td>TUNES DANCE AND POP</td>
    </tr>
    <tr>
        <td>Pop Inglés (2020 - 2010s)💙 Música En Inglés 2010s</td>
    </tr>
    <tr>
        <td>post-teen alternative, indie, pop (large variety)</td>
    </tr>
    <tr>
        <td>Dr. Q&#x27;s Prescription Playlist💊</td>
    </tr>
    <tr>
        <td>BALLARE - رقص</td>
    </tr>
    <tr>
        <td>post teen pop</td>
    </tr>
    <tr>
        <td>Electro Pop | Electropop</td>
    </tr>
    <tr>
        <td>Electropop Hits  2017-2020</td>
    </tr>
    <tr>
        <td>ELECTROPOP</td>
    </tr>
    <tr>
        <td>This Is: Javiera Mena</td>
    </tr>
    <tr>
        <td>ElectroPop 2020</td>
    </tr>
    <tr>
        <td>Electropop - Pop</td>
    </tr>
    <tr>
        <td>This Is Janelle Monáe</td>
    </tr>
    <tr>
        <td>ELECTROPOP🐹</td>
    </tr>
    <tr>
        <td>Electropop And Play</td>
    </tr>
    <tr>
        <td>Mix ElectroPop//ElectroHouse// DeepHouse 2020</td>
    </tr>
    <tr>
        <td>ELECTROPOP EN ESPAÑOL</td>
    </tr>
    <tr>
        <td>Maxi Pop  GOLD (New Wave, Electropop, Synth Pop...)</td>
    </tr>
    <tr>
        <td>Gothic / Industrial / Mittelalter / EBM / Futurepop / Gothik / Electropop</td>
    </tr>
    <tr>
        <td>80&#x27;s Songs | Top 💯 80s Music Hits</td>
    </tr>
    <tr>
        <td>GTA V - Radio Mirror Park</td>
    </tr>
    <tr>
        <td>10er Playlist</td>
    </tr>
    <tr>
        <td>Chillout &amp; Remixes 💜</td>
    </tr>
    <tr>
        <td>POPTIMISM</td>
    </tr>
    <tr>
        <td>The Sound of Indie Poptimism</td>
    </tr>
    <tr>
        <td>Indie/Jazz Poptimism</td>
    </tr>
    <tr>
        <td>The Edge of Indie Poptimism</td>
    </tr>
    <tr>
        <td>2019 in Indie Poptimism</td>
    </tr>
    <tr>
        <td>Indie Poptimism</td>
    </tr>
    <tr>
        <td>A Loose Definition of Indie Poptimism</td>
    </tr>
    <tr>
        <td>The Pulse of Indie Poptimism</td>
    </tr>
    <tr>
        <td>Indie Poptimism!</td>
    </tr>
    <tr>
        <td>indie poptimism</td>
    </tr>
    <tr>
        <td>Music&amp;Other Drugs</td>
    </tr>
    <tr>
        <td>Deep-deep Bubble Pop</td>
    </tr>
    <tr>
        <td>Jazz Vibes</td>
    </tr>
    <tr>
        <td>Lush Lofi</td>
    </tr>
    <tr>
        <td>Lo-Fi Beats</td>
    </tr>
    <tr>
        <td>Lofi Hip-Hop</td>
    </tr>
    <tr>
        <td>Southern California Hip Hop Primer</td>
    </tr>
    <tr>
        <td>90&#x27;s Southern Hip Hop</td>
    </tr>
    <tr>
        <td>90s-2000s Southern Hip Hop / Crunk</td>
    </tr>
    <tr>
        <td>◤ Hip Hop Dance Music – Urban – Trap – Breaking Locking Popping Bopping – WOD – World of Dance</td>
    </tr>
    <tr>
        <td>Badass Rock</td>
    </tr>
    <tr>
        <td>Minitruckin Playlist</td>
    </tr>
    <tr>
        <td>Hip-Hop &#x27;n RnB</td>
    </tr>
    <tr>
        <td>HIP&amp;HOP</td>
    </tr>
    <tr>
        <td>Contemporary Hip Hop</td>
    </tr>
    <tr>
        <td>3rd Coast Classics</td>
    </tr>
    <tr>
        <td>90s Hiphop / Gangsta Rap</td>
    </tr>
    <tr>
        <td>Gangsta Rap 💎 Rap Party</td>
    </tr>
    <tr>
        <td>90&#x27;s Gangster Rap</td>
    </tr>
    <tr>
        <td>RAP Gangsta</td>
    </tr>
    <tr>
        <td>RUSSIAN Gangster Rap</td>
    </tr>
    <tr>
        <td>90s Gangsta Rap / Top Hip-hop Classics</td>
    </tr>
    <tr>
        <td>Rap Party 24/7 Radio / Gangsta Rap</td>
    </tr>
    <tr>
        <td>&lt; DARK TRAP &gt;</td>
    </tr>
    <tr>
        <td>Trapperz Brasil</td>
    </tr>
    <tr>
        <td>Trap Nation</td>
    </tr>
    <tr>
        <td>Trap Mojito</td>
    </tr>
    <tr>
        <td>Arabic Trap</td>
    </tr>
    <tr>
        <td>Sad Trap</td>
    </tr>
    <tr>
        <td>Trap Nation 🔊</td>
    </tr>
    <tr>
        <td>This Is Guns N&#x27; Roses</td>
    </tr>
    <tr>
        <td>The Black Album</td>
    </tr>
    <tr>
        <td>City Pop 1985 シティーポップ</td>
    </tr>
    <tr>
        <td>The Cranberries Best Of</td>
    </tr>
    <tr>
        <td>Vault: Def Leppard Greatest Hits</td>
    </tr>
    <tr>
        <td>80s Pop &amp; Rock Hits and Album Tracks</td>
    </tr>
    <tr>
        <td>Rock and Rios</td>
    </tr>
    <tr>
        <td>Progressive Rock / Metal - Rock /Metal  Progresivo</td>
    </tr>
    <tr>
        <td>House Of The Rising Sun</td>
    </tr>
    <tr>
        <td>Coldplay – Ghost Stories (Deluxe Edition)</td>
    </tr>
    <tr>
        <td>70s Pop &amp; Rock Hits and Deep Tracks</td>
    </tr>
    <tr>
        <td>L&#x27; ALBUM ROCK</td>
    </tr>
    <tr>
        <td>The Queen - La Discografia Completa</td>
    </tr>
    <tr>
        <td>Soda Stereo – El Ultimo Concierto</td>
    </tr>
    <tr>
        <td>The Sound of Album Rock</td>
    </tr>
    <tr>
        <td>Rock Classics</td>
    </tr>
    <tr>
        <td>Classic Rock</td>
    </tr>
    <tr>
        <td>Classic Rock Drive</td>
    </tr>
    <tr>
        <td>Classic Rock Now</td>
    </tr>
    <tr>
        <td>Soft Rock Drive</td>
    </tr>
    <tr>
        <td>Supernatural Classic Rock</td>
    </tr>
    <tr>
        <td>Classic Rock Legends</td>
    </tr>
    <tr>
        <td>Classic Rock 70s 80s 90s, Rock Classics - 70s Rock, 80s Rock, 90s Rock Rock  Classicos</td>
    </tr>
    <tr>
        <td>Southern Rock/Classic Rock</td>
    </tr>
    <tr>
        <td>80s / Classic Rock</td>
    </tr>
    <tr>
        <td>Afro Psychedelica</td>
    </tr>
    <tr>
        <td>Classic Rock Retrogamer</td>
    </tr>
    <tr>
        <td>Workday: Rock Classics</td>
    </tr>
    <tr>
        <td>Classic Rock Greatest Hits</td>
    </tr>
    <tr>
        <td>Blues Rock</td>
    </tr>
    <tr>
        <td>70&#x27;s Classic Rock</td>
    </tr>
    <tr>
        <td>Classic Rock Radio</td>
    </tr>
    <tr>
        <td>Classic Rock Playlist.</td>
    </tr>
    <tr>
        <td>The Sound of Permanent Wave</td>
    </tr>
    <tr>
        <td>Permanent Wave</td>
    </tr>
    <tr>
        <td>Permanent wave 🌊</td>
    </tr>
    <tr>
        <td>permanent wave</td>
    </tr>
    <tr>
        <td>keg party jukebox</td>
    </tr>
    <tr>
        <td>Permanent Wave CHDB</td>
    </tr>
    <tr>
        <td>②⓪①⑨ mixed</td>
    </tr>
    <tr>
        <td>I didn’t know perm stood for permanent (wave)</td>
    </tr>
    <tr>
        <td>Modern Indie Rock // Alternative Rock / Garage Rock / Pop Punk / Grunge / Britpop / Pop Rock</td>
    </tr>
    <tr>
        <td>&quot;Permanent Wave&quot;</td>
    </tr>
    <tr>
        <td>Rock Hard</td>
    </tr>
    <tr>
        <td>Hard Rock</td>
    </tr>
    <tr>
        <td>Hard Rock Workout</td>
    </tr>
    <tr>
        <td>This Is Scorpions</td>
    </tr>
    <tr>
        <td>HARD ROCK CAFE</td>
    </tr>
    <tr>
        <td>Hard Rock Cafe Classics</td>
    </tr>
    <tr>
        <td>Hard Rock Workout!</td>
    </tr>
    <tr>
        <td>Classic Hard Rock</td>
    </tr>
    <tr>
        <td>Workout Hard Rock</td>
    </tr>
    <tr>
        <td>HARD ROCK Vibes</td>
    </tr>
    <tr>
        <td>New Hard Rock</td>
    </tr>
    <tr>
        <td>70s Hard Rock</td>
    </tr>
    <tr>
        <td>Hard Rock Classics 1967-1991 (Party Edition)</td>
    </tr>
    <tr>
        <td>2000&#x27;s hard rock</td>
    </tr>
    <tr>
        <td>Tropical House</td>
    </tr>
    <tr>
        <td>Vibra Tropical</td>
    </tr>
    <tr>
        <td>Tropical Vibes</td>
    </tr>
    <tr>
        <td>Orgulho Tropical</td>
    </tr>
    <tr>
        <td>Sunny Beats</td>
    </tr>
    <tr>
        <td>Tropical Nights</td>
    </tr>
    <tr>
        <td>Tropical House 2020</td>
    </tr>
    <tr>
        <td>Tropical Morning</td>
    </tr>
    <tr>
        <td>EDM TROPICAL</td>
    </tr>
    <tr>
        <td>F**KIN PERFECT</td>
    </tr>
    <tr>
        <td>2020 Hits &amp; 2019  Hits – Top Global Tracks 🔥🔥🔥</td>
    </tr>
    <tr>
        <td>INDIE POP! TUNES</td>
    </tr>
    <tr>
        <td>Great Pops</td>
    </tr>
    <tr>
        <td>Reggaeton Classics</td>
    </tr>
    <tr>
        <td>latin hip hop</td>
    </tr>
    <tr>
        <td>Latin Hip Hop/Freestyle</td>
    </tr>
    <tr>
        <td>Latin Village 2019</td>
    </tr>
    <tr>
        <td>80&#x27;s Freestyle/Disco Dance Party (Set Crossfade to 4-Seconds)</td>
    </tr>
    <tr>
        <td>LATIN FLOW MIX - Música Cristiana🎵</td>
    </tr>
    <tr>
        <td>HIP-HOP: Latin Rap [&#x27;89-present]</td>
    </tr>
    <tr>
        <td>URBAN NATION</td>
    </tr>
    <tr>
        <td>Most Popular 2020 TOP 50</td>
    </tr>
    <tr>
        <td>Top Urban Underground</td>
    </tr>
    <tr>
        <td>Urban contemporary</td>
    </tr>
    <tr>
        <td>urban CONTEMPORARY</td>
    </tr>
    <tr>
        <td>Urban Contemporary</td>
    </tr>
    <tr>
        <td>The 1950s/1960s/1970s/1980s/1990s/2000s/2010s with pop/r&amp;b/soul/boogie/dance/jazz/hip hop/hop/rap.</td>
    </tr>
    <tr>
        <td>Pop Hits 2020</td>
    </tr>
    <tr>
        <td>Ultimate Indie Presents... Best Tracks of 2019</td>
    </tr>
    <tr>
        <td>Charts 2020 🔥Top 2020🔥Hits 2020🔥Summer 2020🔥Pop 2020🔥Popular Music🔥Clean Pop 2020🔥Sing Alongs</td>
    </tr>
    <tr>
        <td>Bluegrass Covers</td>
    </tr>
    <tr>
        <td>Latest Hits 2020 - Pop, Hip Hop &amp; RnB</td>
    </tr>
    <tr>
        <td>Today&#x27;s Hits (Clean)</td>
    </tr>
    <tr>
        <td>Smooth Hip Hop</td>
    </tr>
    <tr>
        <td>Fresh Essentials</td>
    </tr>
    <tr>
        <td>New Jack Swing</td>
    </tr>
    <tr>
        <td>New Jack Swing/ R&amp;B Hits: 1987 - 2002</td>
    </tr>
    <tr>
        <td>Swingbeat (old skool), New Jack Swing, R&amp;B, Hip Hop, Urban</td>
    </tr>
    <tr>
        <td>New Jack City</td>
    </tr>
    <tr>
        <td>90s R&amp;B - The BET Planet Groove/Midnight Love Mix</td>
    </tr>
    <tr>
        <td>Ultimate Throwbacks Collection</td>
    </tr>
    <tr>
        <td>80s-90s R&amp;B / New Jack Swing / Funk / Dance / Soul</td>
    </tr>
    <tr>
        <td>R&amp;B 80&#x27;s/90&#x27;s/00&#x27;s</td>
    </tr>
    <tr>
        <td>Neo Soul Music</td>
    </tr>
    <tr>
        <td>Neo-Soul</td>
    </tr>
    <tr>
        <td>Neo-Soul Guitar</td>
    </tr>
    <tr>
        <td>NEO SOUL GUITAR</td>
    </tr>
    <tr>
        <td>Neo Soul / Modern Jazz / Smooth Hiphop</td>
    </tr>
    <tr>
        <td>NEO-soul</td>
    </tr>
    <tr>
        <td>Groovy // Funky // Neo-Soul</td>
    </tr>
    <tr>
        <td>Neo-Soul / Soulful R&amp;B</td>
    </tr>
    <tr>
        <td>Neo Soul 2019</td>
    </tr>
    <tr>
        <td>NEO FUNK AND SOUL</td>
    </tr>
    <tr>
        <td>Neo Soul</td>
    </tr>
    <tr>
        <td>Japanese Funk/Soul/NEO/Jazz/Acid</td>
    </tr>
    <tr>
        <td>Neo-Jazz Soul RnB &amp; Afro</td>
    </tr>
    <tr>
        <td>Soul Coffee (The Best Neo-Soul Mixtape ever)</td>
    </tr>
    <tr>
        <td>Neo-Soul Essentials</td>
    </tr>
    <tr>
        <td>Electro House 2020</td>
    </tr>
    <tr>
        <td>Electro House Top Tracks</td>
    </tr>
    <tr>
        <td>Nasty Bits</td>
    </tr>
    <tr>
        <td>Electro Posé - Discoveries</td>
    </tr>
    <tr>
        <td>Techno House 2020 👽 Best Collection 👻 Top DJ’s Electronic Music - Deep House - Trance - Tech House - Dance - Electro Pop</td>
    </tr>
    <tr>
        <td>EDM 2020 House &amp; Dance</td>
    </tr>
    <tr>
        <td>Electro Vibes</td>
    </tr>
    <tr>
        <td>Electro Swing Top 100</td>
    </tr>
    <tr>
        <td>Electro Swing</td>
    </tr>
    <tr>
        <td>Electro House</td>
    </tr>
    <tr>
        <td>ELECTRO HOUSE 2020</td>
    </tr>
    <tr>
        <td>New House   ‍</td>
    </tr>
    <tr>
        <td>Jeff Seid Electro House</td>
    </tr>
    <tr>
        <td>Crossfit‏‏​​   ‍</td>
    </tr>
    <tr>
        <td>Electro House - by Spinnin&#x27; Records</td>
    </tr>
    <tr>
        <td>💊ELECTRO-HOUSE-TECH💊</td>
    </tr>
    <tr>
        <td>Fitness Workout Electro | House | Dance | Progressive House</td>
    </tr>
    <tr>
        <td>Club Mix 2020 🍹</td>
    </tr>
    <tr>
        <td>House Electro 2019</td>
    </tr>
    <tr>
        <td>🔊BASSBOOSTED🔊⚡ELECTRO HOUSE⚡🔥EDM CAR MUSIC2018/2019🔥</td>
    </tr>
    <tr>
        <td>Big Room EDM</td>
    </tr>
    <tr>
        <td>Big Room Beast</td>
    </tr>
    <tr>
        <td>Big Room House | Festival Bangers</td>
    </tr>
    <tr>
        <td>PAROOKAVILLE - Big Room</td>
    </tr>
    <tr>
        <td>Big Room House / Bigroom</td>
    </tr>
    <tr>
        <td>Big Room EDM - by Spinnin&#x27; Records</td>
    </tr>
    <tr>
        <td>BIG-ROOM NEVER DIES !</td>
    </tr>
    <tr>
        <td>Dancefloor Beats</td>
    </tr>
    <tr>
        <td>Bounce United</td>
    </tr>
    <tr>
        <td>Locker Room</td>
    </tr>
    <tr>
        <td>Sick Big Room House Drops | EZUMI</td>
    </tr>
    <tr>
        <td>big boom room — TOMORROWLAND EDC EDM BIG ROOM AMF ADE DANCE TRANCE HARDWELL TIESTO</td>
    </tr>
    <tr>
        <td>Trance Party 2019 by FUTURE TRANCE</td>
    </tr>
    <tr>
        <td>SINULOG Festival 2020</td>
    </tr>
    <tr>
        <td>[EAS]: Festival Big Room</td>
    </tr>
    <tr>
        <td>Big Room House</td>
    </tr>
    <tr>
        <td>ALPAS Music Festival</td>
    </tr>
    <tr>
        <td>Epic Bass Drops</td>
    </tr>
    <tr>
        <td>Big Room 2019</td>
    </tr>
    <tr>
        <td>@deniceemoberg EDM - POP REMIXES</td>
    </tr>
    <tr>
        <td>EDM House &amp; Dance</td>
    </tr>
    <tr>
        <td>Pop EDM Remixes</td>
    </tr>
    <tr>
        <td>EDM 2019</td>
    </tr>
    <tr>
        <td>Waves Pop and EDM</td>
    </tr>
    <tr>
        <td>Pop Hits 2000-2019</td>
    </tr>
    <tr>
        <td>EDM - pop remixes</td>
    </tr>
    <tr>
        <td>Pop EDM</td>
    </tr>
    <tr>
        <td>Tastemakers Ball  -  EDM - POP and FUN</td>
    </tr>
    <tr>
        <td>Happy EDM</td>
    </tr>
    <tr>
        <td>EDM/POP</td>
    </tr>
    <tr>
        <td>Selected House</td>
    </tr>
    <tr>
        <td>Deep Electronic Music 2020 &amp; Progressive House</td>
    </tr>
    <tr>
        <td>Vocal House</td>
    </tr>
    <tr>
        <td>Hands Up‏‏​​   ‍</td>
    </tr>
    <tr>
        <td>House/Electro/Progressive/Disco/Lofi/Synthwave</td>
    </tr>
    <tr>
        <td>Alex Workout</td>
    </tr>
    <tr>
        <td>2011-2014 House</td>
    </tr>
    <tr>
        <td>Electro/Progressive/Club House</td>
    </tr>
    <tr>
        <td>CHRISTIAN ELECTRO / DANCE / EDM</td>
    </tr>
    <tr>
        <td>Epic Bass Drops | Best House Mixes</td>
    </tr>
    <tr>
        <td>Brand New EDM</td>
    </tr>
    <tr>
        <td>Gym (Melbourne Bounce/Progressive House)</td>
    </tr>
    <tr>
        <td>Fresh EDM | Progressive House | Electro House | Trap | Deep House | Electronic | Future House/Bass</td>
    </tr>
    <tr>
        <td>Festival Music 2019 - Warm Up Music (EDM, Big Room &amp; Progressive House)</td>
    </tr>
    <tr>
        <td>Underground Party | Hypnotic | Minimal | Acid | Big Room | Tech | Liquid</td>
    </tr>
    <tr>
        <td>Trending EDM by Nik Cooper</td>
    </tr>
    <tr>
        <td>♥ EDM LOVE 2020</td>
    </tr>
</table>



Ta-da! 
