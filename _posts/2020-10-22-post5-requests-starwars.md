---
layout: post
title: Using the `requests` library with the Star Wars API
#gh-repo: oena/oena.github.io
#gh-badge: [star, fork, follow]
tags: [python, requests, API, starwars]
comments: false
readtime: true
--- 

Today, I'll be practicing using the `requests` library by using the library to get data from the Star Wars API. Our eventual goal is to list the films the oldest person/robot/alien was in; for this, we'll need the names, ages, and films from the API's [People resource](https://swapi.dev/documentation#people). 

## 0. Setup


```python
import requests
import pandas as pd
import os 
import re
```

## 1. Use `requests` to download all people from the Star Wars REST API 

Information about the API is available [here](https://swapi.dev/documentation); to start, we'll use `requests` `get` method to obtain the data. 

For starters, let's get the people data: 


```python
base_url = "http://swapi.dev/api"
people_suffix = "people"
```


```python
response = requests.get(os.path.join(base_url, people_suffix))
data = response.json() # get json data 
```


```python
# Look at available keys
data.keys()
```




> dict_keys(['count', 'next', 'previous', 'results'])



It seems like what we're interested in are the results. Let's look at the first result:


```python
data["results"][0]
```




 >   {'name': 'Luke Skywalker',
     'height': '172',
     'mass': '77',
     'hair_color': 'blond',
     'skin_color': 'fair',
     'eye_color': 'blue',
     'birth_year': '19BBY',
     'gender': 'male',
     'homeworld': 'http://swapi.dev/api/planets/1/',
     'films': ['http://swapi.dev/api/films/1/',
      'http://swapi.dev/api/films/2/',
      'http://swapi.dev/api/films/3/',
      'http://swapi.dev/api/films/6/'],
     'species': [],
     'vehicles': ['http://swapi.dev/api/vehicles/14/',
      'http://swapi.dev/api/vehicles/30/'],
     'starships': ['http://swapi.dev/api/starships/12/',
      'http://swapi.dev/api/starships/22/'],
     'created': '2014-12-09T13:50:51.644000Z',
     'edited': '2014-12-20T21:17:56.891000Z',
     'url': 'http://swapi.dev/api/people/1/'}



From here, we see that we'll eventually need to download the film informations from the provided URLs. However, it probably makes sense to only do that for the oldest person (since that's the only entity's film information we're actually interested in). 

So, let's start by identifying the oldest person/alien/robot. 

## 2. Identify oldest person/alien/robot

First, let's start by getting all the `name` and `birth_year` values for each Person entry: 


```python
names_and_ages_dict = {i["name"]: i["birth_year"] for i in data["results"]}
```


```python
# Look at results
names_and_ages_dict
```




>    {'Luke Skywalker': '19BBY',
     'C-3PO': '112BBY',
     'R2-D2': '33BBY',
     'Darth Vader': '41.9BBY',
     'Leia Organa': '19BBY',
     'Owen Lars': '52BBY',
     'Beru Whitesun lars': '47BBY',
     'R5-D4': 'unknown',
     'Biggs Darklighter': '24BBY',
     'Obi-Wan Kenobi': '57BBY'}



According to [the API documentation](https://swapi.dev/documentation#people), "BBY" stands for "Before the Battle of Yavin". So, the oldest person will have the largest number before "BBY" in their age field. 

To get this value, let's just remove the "BBY" suffix from the ages, convert the numeric age values to numbers, and then figure out which person corresponds to the maximum value. 

But before that, let's remove the robot with unknown age, since we don't need this: 


```python
names_and_ages_dict.pop("R5-D4")
```




>    'unknown'




```python
names_and_ages_dict = {name: float(re.sub("BBY$", "", age)) 
    for name, age 
    in names_and_ages_dict.items()}

# inspect
names_and_ages_dict
```




 >   {'Luke Skywalker': 19.0,
     'C-3PO': 112.0,
     'R2-D2': 33.0,
     'Darth Vader': 41.9,
     'Leia Organa': 19.0,
     'Owen Lars': 52.0,
     'Beru Whitesun lars': 47.0,
     'Biggs Darklighter': 24.0,
     'Obi-Wan Kenobi': 57.0}



Ok-- so who is the oldest? 


```python
max(names_and_ages_dict, key=names_and_ages_dict.get)
```




 >   'C-3PO'



## 3. Get films of oldest person (robot): C-3PO

Almost done! Lastly, let's download C-3PO's movies and list those (along with his name): 


```python
# Start a new dictionary to store results to output
c3po_dict = {"Name": max(names_and_ages_dict, key=names_and_ages_dict.get),
             "Films" : []}
```


```python
# Get index of C-3PO's results from original request 
c3po_index = [i for i in range(0,len(data["results"])) if data["results"][i]["name"] == "C-3PO"][0]

# Download film titles
for i in range(0, len(data["results"][c3po_index]["films"])):
    film = requests.get(data["results"][c3po_index]["films"][i])
    film_title = film.json()["title"]
    c3po_dict["Films"].append(film_title)
```


```python
c3po_dict
```




 >   {'Name': 'C-3PO',
     'Films': ['A New Hope',
      'The Empire Strikes Back',
      'Return of the Jedi',
      'The Phantom Menace',
      'Attack of the Clones',
      'Revenge of the Sith']}



And there we have it! 
