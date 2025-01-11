[![](https://img.shields.io/badge/bumi_1.0.0-passing-green)](https://github.com/gongahkia/bumi/releases/tag/1.0.0) 

# `Bumi`

Quick and dirty [Letterboxd](https://letterboxd.com/) profile scraper.

Bumi is open-source and authentication-free.

Implemented in [2 hours and 11 minutes]().

## Usage

1. Clone [`Bumi`](https://github.com/gongahkia/bumi) within your codebase.

```console
$ git clone https://github.com/gongahkia/bumi
```

2. Call `scrape_letterboxd_user()`.

```py
import bumi

USER_LETTERBOXD_PROFILE = "https://letterboxd.com/<user_profile>/"
result = bumi.scrape_letterboxd_user(USER_LETTERBOXD_PROFILE)
```

3. Scraped output is returned as a dictionary.

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

## Reference

The name `Bumi` is in reference to [King Bumi](https://avatar.fandom.com/wiki/Bumi_(King_of_Omashu)), the elderly [King](https://avatar.fandom.com/wiki/Monarch_of_Omashu) of [Omashu](https://avatar.fandom.com/wiki/Omashu) who was a childhood friend of the [Avatar](https://avatar.fandom.com/wiki/Avatar) [Aang](https://avatar.fandom.com/wiki/Aang) prior to the [Hundred Year War](https://avatar.fandom.com/wiki/Hundred_Year_War). He first appears in the fifth episode of [Book One: Water](https://avatar.fandom.com/wiki/Book_One:_Water) under the Nickelodeon series [Avatar: The Last Airbender](https://avatar.fandom.com/wiki/Avatar:_The_Last_Airbender).

![](./asset/bumi.png)