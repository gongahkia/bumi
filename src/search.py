# ----- FILM SEARCH -----

import urllib.parse
from playwright.sync_api import sync_playwright


def search_films(query, max_results=20):
    """
    searches letterboxd for films by title

    Args:
        query: search query string
        max_results: maximum number of results to return

    Returns:
        list of film results with title, year, slug, and poster
    """
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://letterboxd.com/search/films/{encoded_query}/"
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(search_url)
            print(f"Success: Searching for '{query}'")

            film_results = page.query_selector_all("ul.results li.film-detail")

            for i, item in enumerate(film_results):
                if i >= max_results:
                    break

                film_data = {
                    "title": None,
                    "year": None,
                    "film_slug": None,
                    "director": None,
                    "poster_url": None,
                }

                poster = item.query_selector("div.film-poster")
                if poster:
                    film_data["film_slug"] = poster.get_attribute("data-film-slug")
                    img = poster.query_selector("img")
                    if img:
                        film_data["poster_url"] = img.get_attribute("src")

                title_el = item.query_selector("h2.headline-2 a")
                if title_el:
                    film_data["title"] = title_el.inner_text().strip()

                year_el = item.query_selector("h2.headline-2 small a")
                if year_el:
                    film_data["year"] = year_el.inner_text().strip()

                director_el = item.query_selector("p.film-detail-content a")
                if director_el:
                    film_data["director"] = director_el.inner_text().strip()

                results.append(film_data)

        except Exception as e:
            print(f"Error searching for '{query}': {e}")
        page.close()
        browser.close()

    return results


def search_films_advanced(query, filters=None, max_results=20):
    """
    advanced film search with filters

    Args:
        query: search query string
        filters: dict with optional filters:
            - decade: e.g., "2020s", "1990s"
            - genre: e.g., "horror", "comedy"
            - year: specific year
        max_results: maximum results to return

    Returns:
        list of film results
    """
    base_url = "https://letterboxd.com/films/"

    if filters:
        if filters.get("decade"):
            base_url += f"decade/{filters['decade']}/"
        if filters.get("genre"):
            base_url += f"genre/{filters['genre']}/"
        if filters.get("year"):
            base_url += f"year/{filters['year']}/"

    search_url = base_url
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(search_url)
            print(f"Success: Advanced search at {search_url}")

            posters = page.query_selector_all("li.poster-container")

            for i, poster_container in enumerate(posters):
                if i >= max_results:
                    break

                film_data = {
                    "title": None,
                    "film_slug": None,
                    "poster_url": None,
                }

                poster = poster_container.query_selector("div.film-poster")
                if poster:
                    film_data["title"] = poster.get_attribute("data-film-name")
                    film_data["film_slug"] = poster.get_attribute("data-film-slug")

                img = poster_container.query_selector("img")
                if img:
                    film_data["poster_url"] = img.get_attribute("src")

                if film_data["title"]:
                    results.append(film_data)

        except Exception as e:
            print(f"Error in advanced search: {e}")
        page.close()
        browser.close()

    return results


def get_popular_films(time_period="week", max_results=20):
    """
    gets popular films on letterboxd

    Args:
        time_period: 'week', 'month', or 'year'
        max_results: maximum results to return

    Returns:
        list of popular films
    """
    period_map = {
        "week": "this/week/",
        "month": "this/month/",
        "year": "this/year/",
    }

    period_path = period_map.get(time_period, "this/week/")
    url = f"https://letterboxd.com/films/popular/{period_path}"
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url)
            print(f"Success: Getting popular films for {time_period}")

            posters = page.query_selector_all("li.poster-container")

            for i, poster_container in enumerate(posters):
                if i >= max_results:
                    break

                film_data = {
                    "title": None,
                    "film_slug": None,
                    "poster_url": None,
                    "rank": i + 1,
                }

                poster = poster_container.query_selector("div.film-poster")
                if poster:
                    film_data["title"] = poster.get_attribute("data-film-name")
                    film_data["film_slug"] = poster.get_attribute("data-film-slug")

                img = poster_container.query_selector("img")
                if img:
                    film_data["poster_url"] = img.get_attribute("src")

                if film_data["title"]:
                    results.append(film_data)

        except Exception as e:
            print(f"Error getting popular films: {e}")
        page.close()
        browser.close()

    return results


# ----- ACTIVITY FEED -----


def scrape_activity_feed(target_url, max_items=50):
    """
    scrapes activity feed from user's followed accounts

    Args:
        target_url: letterboxd user profile URL
        max_items: maximum number of activity items to return

    Returns:
        list of activity items
    """
    feed_url = f"{target_url}activity/"
    activities = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(feed_url)
            print(f"Success: Retrieved activity feed {feed_url}")

            activity_items = page.query_selector_all("section.activity-row")

            for i, item in enumerate(activity_items):
                if i >= max_items:
                    break

                activity_data = {
                    "type": None,
                    "user": None,
                    "film_name": None,
                    "film_slug": None,
                    "rating": None,
                    "review_snippet": None,
                }

                user_link = item.query_selector("a.avatar")
                if user_link:
                    activity_data["user"] = user_link.get_attribute("href").strip("/")

                poster = item.query_selector("div.film-poster")
                if poster:
                    activity_data["film_name"] = poster.get_attribute("data-film-name")
                    activity_data["film_slug"] = poster.get_attribute("data-film-slug")

                rating_el = item.query_selector("span.rating")
                if rating_el:
                    activity_data["rating"] = rating_el.inner_text().strip()
                    activity_data["type"] = "rating"

                review_el = item.query_selector("div.body-text")
                if review_el:
                    activity_data["review_snippet"] = review_el.inner_text().strip()[:200]
                    activity_data["type"] = "review"

                if not activity_data["type"]:
                    activity_data["type"] = "activity"

                activities.append(activity_data)

        except Exception as e:
            print(f"Error getting activity feed: {e}")
        page.close()
        browser.close()

    return activities


def scrape_popular_reviews(film_slug, max_reviews=20):
    """
    scrapes popular reviews for a film

    Args:
        film_slug: letterboxd film slug
        max_reviews: maximum number of reviews to return

    Returns:
        list of popular reviews
    """
    reviews_url = f"https://letterboxd.com/film/{film_slug}/reviews/by/activity/"
    reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(reviews_url)
            print(f"Success: Getting popular reviews for {film_slug}")

            review_items = page.query_selector_all("li.film-detail")

            for i, item in enumerate(review_items):
                if i >= max_reviews:
                    break

                review_data = {
                    "user": None,
                    "rating": None,
                    "review_text": None,
                    "likes_count": None,
                    "date": None,
                }

                user_link = item.query_selector("a.avatar")
                if user_link:
                    review_data["user"] = user_link.get_attribute("href").strip("/")

                rating_el = item.query_selector("span.rating")
                if rating_el:
                    review_data["rating"] = rating_el.inner_text().strip()

                review_body = item.query_selector("div.body-text")
                if review_body:
                    review_data["review_text"] = review_body.inner_text().strip()

                date_el = item.query_selector("span.date a")
                if date_el:
                    review_data["date"] = date_el.inner_text().strip()

                reviews.append(review_data)

        except Exception as e:
            print(f"Error getting popular reviews: {e}")
        page.close()
        browser.close()

    return reviews
