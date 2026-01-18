# Bumi Usage Guide

## Installation

```bash
pip install playwright
playwright install
pip install fastapi uvicorn  # optional, for API server
```

## Quick Start

```python
from src import scrape_letterboxd

# Scrape a user profile
data = scrape_letterboxd("https://letterboxd.com/username/")
print(data)
```

## Core Scraping Functions

```python
from src import (
    scrape_letterboxd,           # Full profile + watchlist + all films
    scrape_letterboxd_user,      # Profile only (name, bio, stats, favourites)
    scrape_letterboxd_user_films,# All watched films
    scrape_letterboxd_user_watchlist,  # Watchlist
    scrape_user_diary,           # Watch diary with dates
    scrape_user_reviews,         # User's reviews
    scrape_user_lists,           # User's lists
    scrape_list_contents,        # Films in a specific list
    scrape_user_followers,       # Followers
    scrape_user_following,       # Following
    scrape_film_details,         # Single film details
)

# Examples
films = scrape_letterboxd_user_films("https://letterboxd.com/username/", paginate=True, max_pages=100)
diary = scrape_user_diary("https://letterboxd.com/username/", paginate=True, max_pages=50)
film = scrape_film_details("the-godfather")
```

## User Comparison

```python
from src import compare_users, find_watch_recommendations

# Compare two users
result = compare_users("user1", "user2")
print(result["statistics"])           # Counts and compatibility %
print(result["common_films"])         # Films both watched
print(result["unique_to_user1"])      # Only user1 watched
print(result["unique_to_user2"])      # Only user2 watched

# Get recommendations (films user2 watched that user1 hasn't)
recs = find_watch_recommendations("user1", "user2")
print(recs["films"])
```

## Search

```python
from src import search_films, search_films_advanced, get_popular_films

# Basic search
results = search_films("inception", max_results=10)

# Advanced search with filters
results = search_films_advanced("", filters={"decade": "2020s", "genre": "horror"})

# Popular films
popular = get_popular_films(time_period="week")  # week, month, year
```

## Data Export

```python
from src import export_data, export_to_json, export_to_csv, export_to_xml

data = scrape_letterboxd("https://letterboxd.com/username/")

export_data(data, "output", format="json")  # output.json
export_data(data, "output", format="csv")   # output.csv
export_data(data, "output", format="xml")   # output.xml
```

## Storage (SQLite/PostgreSQL)

```python
from src import SQLiteStorage, PostgreSQLStorage

# SQLite
with SQLiteStorage("bumi.db") as db:
    db.save_user(user_data)
    db.save_film(film_data)
    user = db.get_user("username")

# PostgreSQL
with PostgreSQLStorage(host="localhost", database="bumi", user="postgres", password="pass") as db:
    db.save_user(user_data)
```

## Caching

```python
from src import cache_get, cache_set, cache_clear

cache_set("key", data)
cached = cache_get("key", ttl=3600)  # 1 hour TTL
cache_clear()  # Clear all
```

## Snapshots & Diff

```python
from src import save_snapshot, load_latest_snapshot, detect_profile_changes

# Save snapshot
save_snapshot(data, "username")

# Load and compare
old_data, path = load_latest_snapshot("username")
changes = detect_profile_changes(old_data, new_data)
print(changes["has_changes"])
print(changes["watchlist_changes"])
```

## Batch Scraping

```python
from src import batch_scrape_users, aggregate_batch_results

results = batch_scrape_users(["user1", "user2", "user3"])
stats = aggregate_batch_results(results)
print(stats["total_films_watched"])
```

## Webhooks

```python
from src import register_webhook, scrape_with_webhook

# Register webhook
register_webhook("https://yourserver.com/webhook", events=["scrape_complete"])

# Scrape with notification
result = scrape_with_webhook("https://letterboxd.com/username/")
```

## REST API Server

```bash
# Start server
make serve
# or
uvicorn server:app --host 0.0.0.0 --port 8000

# Deploy to Render
# Push repo, Render auto-detects render.yaml
```

### API Endpoints

```
GET  /                         # Root
GET  /health                   # Health check
GET  /scrape/user/{username}   # Scrape user profile
GET  /scrape/watchlist/{username}
GET  /scrape/diary/{username}
GET  /scrape/reviews/{username}
GET  /scrape/film/{film_slug}
GET  /validate/{username}
GET  /check/{username}         # Check if profile exists
POST /scrape/user              # Body: {"username": "x", "paginate": true}
POST /scrape/batch             # Body: {"usernames": ["x","y"]}
POST /scrape/film              # Body: {"film_slug": "the-godfather"}
```

## Configuration

```python
from src import set_timeouts, set_rate_limit

# Timeouts (milliseconds)
set_timeouts(page_load=30000, element_wait=10000)

# Rate limiting (seconds)
set_rate_limit(min_delay=1.0, max_delay=2.0, randomize=True)
```

## Browser Pool (Concurrent Scraping)

```python
from src import BrowserPool

with BrowserPool(pool_size=3, headless=True) as pool:
    browser = pool.acquire()
    # use browser
    pool.release(browser)
```

## Custom CSS Selectors

```python
from src import set_selector, load_selectors_from_file, save_selectors_to_file

set_selector("profile", "bio", "div.custom-bio-selector")
save_selectors_to_file("selectors.json")
load_selectors_from_file("selectors.json")
```
