[![](https://img.shields.io/badge/bumi_1.0.0-passing-light_green)](https://github.com/gongahkia/bumi/releases/tag/1.0.0) 
[![](https://img.shields.io/badge/bumi_2.0.0-passing-green)](https://github.com/gongahkia/bumi/releases/tag/2.0.0) 

# `Bumi`

Quick and dirty [Letterboxd](https://letterboxd.com/) profile scraper.

First implemented in [1 hour and 47 minutes](https://github.com/gongahkia/bumi/commit/01a5cb7572e1df6f4f3b13bccbf42262fb16f579).

<div align="center">
    <img src="./asset/bumi.png">
</div>

## Rationale 

[Letterboxd's official API](https://api-docs.letterboxd.com/) is [closed-source](https://www.reddit.com/r/Letterboxd/comments/knu50f/has_anybody_tried_using_the_letterboxd_api/) and requires [oauth2](https://api-docs.letterboxd.com/#auth).

[`Bumi`](https://github.com/gongahkia/bumi) is open-source and authentication-free.

## Usage

1. Clone [`Bumi`](https://github.com/gongahkia/bumi) within your codebase.

```console
$ git clone https://github.com/gongahkia/bumi && cd bumi
$ pip install fastapi uvicorn playwright 
$ playwright install 
```

2. Then call `scrape_letterboxd()` (or `Bumi`'s other core functions) directly within your project.

```py
from bumi.src import (
    scrape_letterboxd,           
    scrape_letterboxd_user,      
    scrape_letterboxd_user_films,
    scrape_letterboxd_user_watchlist,  
    scrape_user_diary,           
    scrape_user_reviews,         
    scrape_user_lists,           
    scrape_list_contents,        
    scrape_user_followers,       
    scrape_user_following,       
    scrape_film_details,         
)

USER_LETTERBOXD_PROFILE = "https://letterboxd.com/<user_profile>/"
FILM_NAME = "the-godfather"
profile = bumi.scrape_letterboxd(USER_LETTERBOXD_PROFILE)
films = scrape_letterboxd_user_films(USER_LETTERBOXD_PROFILE, paginate=True, max_pages=100)
diary = scrape_user_diary(USER_LETTERBOXD_PROFILE, paginate=True, max_pages=50)
film = scrape_film_details(FILM_NAME)
```

Note that scraped output is returned as a dictionary with the below schema.

```json
user_data = {
    "metadata": {
        "date_time": "",
        "target_url": "",
        "duration": "",
    },
    "scraped_data": {
        "profile": {
            "user_name": "",
            "user_data_person": "",
            "user_bio": "",
            "user_statistics": "",
            "user_profile_image": "",
        },
        "films": {
            "favourite_films": [],
            "recent_activity": [],
            "watchlist": [],
        },
    },
}
```

3. Alternatively, run `Bumi` backend as a REST API Server.

```console
$ make serve
$ uvicorn server:app --host 0.0.0.0 --port 8000
```

It serves the following `GET` and `POST` endpoints.

* ***GET*** endpoints
    * `GET  /`: Root
    * `GET  /health`: Health check
    * `GET  /scrape/user/{username}`: Scrape user profile
    * `GET  /scrape/watchlist/{username}`: Scrape user watchlist
    * `GET  /scrape/diary/{username}`: Scrape user diary
    * `GET  /scrape/reviews/{username}`: Scrape user reviews
    * `GET  /scrape/film/{film_slug}`: Scrape film summary
    * `GET  /validate/{username}`: Validate profile activity
    * `GET  /check/{username}`: Check if profile exists
* ***POST*** endpoints
    * `POST /scrape/user`: Body: {"username": "x", "paginate": true}
    * `POST /scrape/batch`: Body: {"usernames": ["x","y"]}
    * `POST /scrape/film`: Body: {"film_slug": "the-godfather"}

## Reference

The name `Bumi` is in reference to [King Bumi](https://avatar.fandom.com/wiki/Bumi_(King_of_Omashu)), the elderly [King](https://avatar.fandom.com/wiki/Monarch_of_Omashu) of [Omashu](https://avatar.fandom.com/wiki/Omashu) who was a childhood friend of the [Avatar](https://avatar.fandom.com/wiki/Avatar) [Aang](https://avatar.fandom.com/wiki/Aang) prior to the [Hundred Year War](https://avatar.fandom.com/wiki/Hundred_Year_War). He first appears in the fifth episode of [Book One: Water](https://avatar.fandom.com/wiki/Book_One:_Water) under the Nickelodeon series [Avatar: The Last Airbender](https://avatar.fandom.com/wiki/Avatar:_The_Last_Airbender).