# ----- REQUIRED IMPORTS -----

import os
import time
import json
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright


# ----- CACHING SYSTEM -----

CACHE_DIR = Path.home() / ".bumi_cache"
DEFAULT_TTL = 3600  # 1 hour in seconds


def _get_cache_path(cache_key):
    """returns the file path for a cache entry"""
    CACHE_DIR.mkdir(exist_ok=True)
    hashed_key = hashlib.md5(cache_key.encode()).hexdigest()
    return CACHE_DIR / f"{hashed_key}.json"


def cache_get(cache_key, ttl=DEFAULT_TTL):
    """retrieves cached data if it exists and hasn't expired"""
    cache_path = _get_cache_path(cache_key)
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r") as f:
            cached = json.load(f)
        cached_time = cached.get("timestamp", 0)
        if time.time() - cached_time > ttl:
            cache_path.unlink()
            return None
        return cached.get("data")
    except (json.JSONDecodeError, IOError):
        return None


def cache_set(cache_key, data):
    """stores data in cache with current timestamp"""
    cache_path = _get_cache_path(cache_key)
    CACHE_DIR.mkdir(exist_ok=True)
    try:
        with open(cache_path, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
    except IOError as e:
        print(f"Warning: Failed to write cache: {e}")


def cache_clear():
    """clears all cached data"""
    if CACHE_DIR.exists():
        for cache_file in CACHE_DIR.glob("*.json"):
            cache_file.unlink()
        print("Cache cleared successfully")


def cache_clear_expired(ttl=DEFAULT_TTL):
    """removes expired cache entries"""
    if not CACHE_DIR.exists():
        return
    current_time = time.time()
    for cache_file in CACHE_DIR.glob("*.json"):
        try:
            with open(cache_file, "r") as f:
                cached = json.load(f)
            if current_time - cached.get("timestamp", 0) > ttl:
                cache_file.unlink()
        except (json.JSONDecodeError, IOError):
            cache_file.unlink()


# ----- TIMEOUT CONFIGURATION -----

class TimeoutConfig:
    """
    configurable timeout settings for scraping operations
    """

    def __init__(
        self,
        page_load_timeout=30000,
        element_wait_timeout=10000,
        navigation_timeout=30000,
        script_timeout=30000,
    ):
        """
        Args:
            page_load_timeout: timeout for page load in milliseconds
            element_wait_timeout: timeout for element waits in milliseconds
            navigation_timeout: timeout for navigation in milliseconds
            script_timeout: timeout for script execution in milliseconds
        """
        self.page_load_timeout = page_load_timeout
        self.element_wait_timeout = element_wait_timeout
        self.navigation_timeout = navigation_timeout
        self.script_timeout = script_timeout


# global timeout configuration
_timeout_config = TimeoutConfig()


def set_timeouts(
    page_load=30000, element_wait=10000, navigation=30000, script=30000
):
    """configures global timeout settings"""
    global _timeout_config
    _timeout_config = TimeoutConfig(page_load, element_wait, navigation, script)


def get_timeout_config():
    """returns current timeout configuration"""
    return _timeout_config


def apply_timeouts_to_page(page):
    """applies timeout configuration to a playwright page"""
    config = get_timeout_config()
    page.set_default_timeout(config.element_wait_timeout)
    page.set_default_navigation_timeout(config.navigation_timeout)


def safe_goto(page, url, timeout=None):
    """
    navigates to URL with timeout handling

    Args:
        page: playwright page object
        url: URL to navigate to
        timeout: optional timeout override in milliseconds

    Returns:
        response object if successful, None on timeout
    """
    config = get_timeout_config()
    effective_timeout = timeout or config.page_load_timeout
    try:
        response = page.goto(url, timeout=effective_timeout)
        return response
    except Exception as e:
        if "timeout" in str(e).lower():
            print(f"Timeout loading {url} after {effective_timeout}ms")
        else:
            print(f"Error loading {url}: {e}")
        return None


def safe_wait_for_selector(page, selector, timeout=None):
    """
    waits for element with timeout handling

    Args:
        page: playwright page object
        selector: CSS selector to wait for
        timeout: optional timeout override in milliseconds

    Returns:
        element if found, None on timeout
    """
    config = get_timeout_config()
    effective_timeout = timeout or config.element_wait_timeout
    try:
        return page.wait_for_selector(selector, timeout=effective_timeout)
    except Exception as e:
        if "timeout" in str(e).lower():
            print(f"Timeout waiting for {selector} after {effective_timeout}ms")
        return None


# ----- BROWSER POOL -----

class BrowserPool:
    """
    manages a pool of browser instances for concurrent scraping
    """

    def __init__(self, pool_size=3, headless=True):
        """
        Args:
            pool_size: number of browser instances in pool
            headless: whether browsers run in headless mode
        """
        self.pool_size = pool_size
        self.headless = headless
        self._playwright = None
        self._browsers = []
        self._available = []
        self._in_use = set()

    def start(self):
        """initializes the browser pool"""
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        for _ in range(self.pool_size):
            browser = self._playwright.chromium.launch(headless=self.headless)
            self._browsers.append(browser)
            self._available.append(browser)
        print(f"Browser pool started with {self.pool_size} instances")

    def acquire(self):
        """acquires a browser from the pool, blocks if none available"""
        while not self._available:
            time.sleep(0.1)
        browser = self._available.pop()
        self._in_use.add(browser)
        return browser

    def release(self, browser):
        """returns a browser to the pool"""
        if browser in self._in_use:
            self._in_use.remove(browser)
            self._available.append(browser)

    def close(self):
        """closes all browsers and playwright"""
        for browser in self._browsers:
            try:
                browser.close()
            except Exception:
                pass
        if self._playwright:
            self._playwright.stop()
        self._browsers.clear()
        self._available.clear()
        self._in_use.clear()
        print("Browser pool closed")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


# global browser pool instance (initialized on demand)
_browser_pool = None


def get_browser_pool(pool_size=3, headless=True):
    """gets or creates the global browser pool"""
    global _browser_pool
    if _browser_pool is None:
        _browser_pool = BrowserPool(pool_size, headless)
        _browser_pool.start()
    return _browser_pool


def close_browser_pool():
    """closes the global browser pool"""
    global _browser_pool
    if _browser_pool:
        _browser_pool.close()
        _browser_pool = None


# ----- RATE LIMITING -----

class RateLimiter:
    """
    rate limiter with configurable delays between requests
    """

    def __init__(self, min_delay=1.0, max_delay=3.0, randomize=True):
        """
        Args:
            min_delay: minimum delay between requests in seconds
            max_delay: maximum delay for randomized delays
            randomize: if True, uses random delay between min and max
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.randomize = randomize
        self.last_request_time = 0

    def wait(self):
        """waits appropriate time before next request"""
        import random
        elapsed = time.time() - self.last_request_time
        if self.randomize:
            delay = random.uniform(self.min_delay, self.max_delay)
        else:
            delay = self.min_delay
        remaining = delay - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self.last_request_time = time.time()

    def reset(self):
        """resets the rate limiter"""
        self.last_request_time = 0


# global rate limiter instance with polite defaults
_rate_limiter = RateLimiter(min_delay=1.0, max_delay=2.0)


def set_rate_limit(min_delay=1.0, max_delay=2.0, randomize=True):
    """configures the global rate limiter"""
    global _rate_limiter
    _rate_limiter = RateLimiter(min_delay, max_delay, randomize)


def rate_limit_wait():
    """applies rate limiting delay before a request"""
    _rate_limiter.wait()


# ----- RETRY MECHANISM -----

def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=30.0, exceptions=(Exception,)):
    """
    executes a function with exponential backoff retry logic

    Args:
        func: callable to execute
        max_retries: maximum number of retry attempts
        base_delay: initial delay in seconds
        max_delay: maximum delay between retries
        exceptions: tuple of exceptions to catch and retry

    Returns:
        result of func if successful, None if all retries fail
    """
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                delay = min(base_delay * (2 ** attempt), max_delay)
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed. Last error: {e}")
    return None


def make_request_with_retry(page, url, max_retries=3, base_delay=1.0):
    """
    navigates to a URL with retry logic for transient failures

    Args:
        page: playwright page object
        url: URL to navigate to
        max_retries: maximum retry attempts
        base_delay: initial backoff delay

    Returns:
        True if successful, False otherwise
    """
    for attempt in range(max_retries + 1):
        try:
            response = page.goto(url)
            if response and response.ok:
                return True
            if response and response.status >= 500:
                raise Exception(f"Server error: {response.status}")
            return True
        except Exception as e:
            if attempt < max_retries:
                delay = min(base_delay * (2 ** attempt), 30.0)
                print(f"Request failed (attempt {attempt + 1}): {e}. Retrying in {delay:.1f}s...")
                time.sleep(delay)
            else:
                print(f"Request failed after {max_retries + 1} attempts: {e}")
                return False
    return False


# ----- HELPER FUNCTIONS -----


def scrape_film_details(film_slug):
    """
    scrapes detailed information for a specific film from letterboxd
    """
    film_url = f"https://letterboxd.com/film/{film_slug}/"
    film_details = {
        "film_slug": film_slug,
        "title": None,
        "year": None,
        "director": None,
        "runtime": None,
        "genres": [],
        "average_rating": None,
        "tagline": None,
        "description": None,
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(film_url)
            print(f"Success: Retrieved film page {film_url}")

            header = page.query_selector("section.film-header-group")
            if header:
                title_el = header.query_selector("h1.headline-1")
                if title_el:
                    film_details["title"] = title_el.inner_text().strip()
                year_el = header.query_selector("small.number a")
                if year_el:
                    film_details["year"] = year_el.inner_text().strip()
                director_el = header.query_selector("span.directorlist a")
                if director_el:
                    film_details["director"] = director_el.inner_text().strip()

            tagline_el = page.query_selector("h4.tagline")
            if tagline_el:
                film_details["tagline"] = tagline_el.inner_text().strip()

            desc_el = page.query_selector("div.truncate p")
            if desc_el:
                film_details["description"] = desc_el.inner_text().strip()

            sidebar = page.query_selector("aside.sidebar")
            if sidebar:
                runtime_el = sidebar.query_selector("p.text-link")
                if runtime_el:
                    runtime_text = runtime_el.inner_text().strip()
                    if "mins" in runtime_text.lower():
                        film_details["runtime"] = runtime_text

            genre_els = page.query_selector_all("div#tab-genres a.text-slug")
            film_details["genres"] = [g.inner_text().strip() for g in genre_els]

            rating_el = page.query_selector("a.tooltip.display-rating")
            if rating_el:
                rating_text = rating_el.inner_text().strip()
                film_details["average_rating"] = rating_text

        except Exception as e:
            print(f"Error: Unable to process film {film_slug}: {e}")
        page.close()
        browser.close()

    return film_details


def scrape_user_reviews(target_url, paginate=True, max_pages=50):
    """
    scrapes user's film reviews with ratings from letterboxd
    """
    base_reviews_url = f"{target_url}films/reviews/"
    reviews_array = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        current_page = 1
        try:
            while True:
                if current_page == 1:
                    page_url = base_reviews_url
                else:
                    page_url = f"{base_reviews_url}page/{current_page}/"
                page.goto(page_url)
                print(f"Success: Retrieved reviews page {page_url}")

                review_items = page.query_selector_all("li.film-detail")
                if not review_items:
                    break

                for item in review_items:
                    review_data = {
                        "film_name": None,
                        "film_slug": None,
                        "rating": None,
                        "review_text": None,
                        "review_date": None,
                        "liked": False,
                    }

                    poster = item.query_selector("div.film-poster")
                    if poster:
                        review_data["film_name"] = poster.get_attribute("data-film-name")
                        review_data["film_slug"] = poster.get_attribute("data-film-slug")

                    rating_el = item.query_selector("span.rating")
                    if rating_el:
                        review_data["rating"] = rating_el.inner_text().strip()

                    review_body = item.query_selector("div.body-text")
                    if review_body:
                        review_data["review_text"] = review_body.inner_text().strip()

                    date_el = item.query_selector("span.date a")
                    if date_el:
                        review_data["review_date"] = date_el.inner_text().strip()

                    like_el = item.query_selector("span.like.icon-liked")
                    if like_el:
                        review_data["liked"] = True

                    reviews_array.append(review_data)

                if not paginate:
                    break

                next_link = page.query_selector("a.next")
                if not next_link or current_page >= max_pages:
                    break
                current_page += 1

        except Exception as e:
            print(f"Error: Unable to process reviews page {current_page}: {e}")
        page.close()
        browser.close()

    return reviews_array


def scrape_user_diary(target_url, paginate=True, max_pages=100):
    """
    scrapes user's film diary with watch dates and rewatch info from letterboxd
    """
    base_diary_url = f"{target_url}films/diary/"
    diary_entries = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        current_page = 1
        try:
            while True:
                if current_page == 1:
                    page_url = base_diary_url
                else:
                    page_url = f"{base_diary_url}page/{current_page}/"
                page.goto(page_url)
                print(f"Success: Retrieved diary page {page_url}")

                entries = page.query_selector_all("tr.diary-entry-row")
                if not entries:
                    break

                for entry in entries:
                    entry_data = {
                        "film_name": None,
                        "film_slug": None,
                        "watch_date": None,
                        "rating": None,
                        "rewatch": False,
                        "liked": False,
                        "has_review": False,
                    }

                    poster = entry.query_selector("td.td-film-details div.film-poster")
                    if poster:
                        entry_data["film_name"] = poster.get_attribute("data-film-name")
                        entry_data["film_slug"] = poster.get_attribute("data-film-slug")

                    date_el = entry.query_selector("td.td-calendar a")
                    if date_el:
                        entry_data["watch_date"] = date_el.get_attribute("href")

                    rating_el = entry.query_selector("td.td-rating span.rating")
                    if rating_el:
                        entry_data["rating"] = rating_el.inner_text().strip()

                    rewatch_el = entry.query_selector("td.td-rewatch span.icon-status-rewatch")
                    if rewatch_el:
                        entry_data["rewatch"] = True

                    like_el = entry.query_selector("td.td-like span.icon-liked")
                    if like_el:
                        entry_data["liked"] = True

                    review_el = entry.query_selector("td.td-review a.icon-review")
                    if review_el:
                        entry_data["has_review"] = True

                    diary_entries.append(entry_data)

                if not paginate:
                    break

                next_link = page.query_selector("a.next")
                if not next_link or current_page >= max_pages:
                    break
                current_page += 1

        except Exception as e:
            print(f"Error: Unable to process diary page {current_page}: {e}")
        page.close()
        browser.close()

    return diary_entries


def scrape_user_lists(target_url, paginate=True, max_pages=20):
    """
    scrapes all lists created by a user from letterboxd
    """
    base_lists_url = f"{target_url}lists/"
    lists_array = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        current_page = 1
        try:
            while True:
                if current_page == 1:
                    page_url = base_lists_url
                else:
                    page_url = f"{base_lists_url}page/{current_page}/"
                page.goto(page_url)
                print(f"Success: Retrieved lists page {page_url}")

                list_items = page.query_selector_all("section.list-set")
                if not list_items:
                    break

                for item in list_items:
                    list_data = {
                        "list_name": None,
                        "list_url": None,
                        "description": None,
                        "film_count": None,
                    }

                    title_el = item.query_selector("h2.title a")
                    if title_el:
                        list_data["list_name"] = title_el.inner_text().strip()
                        list_data["list_url"] = title_el.get_attribute("href")

                    desc_el = item.query_selector("div.body-text p")
                    if desc_el:
                        list_data["description"] = desc_el.inner_text().strip()

                    count_el = item.query_selector("small.value")
                    if count_el:
                        list_data["film_count"] = count_el.inner_text().strip()

                    lists_array.append(list_data)

                if not paginate:
                    break

                next_link = page.query_selector("a.next")
                if not next_link or current_page >= max_pages:
                    break
                current_page += 1

        except Exception as e:
            print(f"Error: Unable to process lists page {current_page}: {e}")
        page.close()
        browser.close()

    return lists_array


def scrape_list_contents(list_url, paginate=True, max_pages=50):
    """
    scrapes all films from a specific letterboxd list
    """
    full_url = f"https://letterboxd.com{list_url}" if list_url.startswith("/") else list_url
    list_contents = {
        "list_url": list_url,
        "films": [],
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        current_page = 1
        try:
            while True:
                if current_page == 1:
                    page_url = full_url
                else:
                    page_url = f"{full_url}page/{current_page}/"
                page.goto(page_url)
                print(f"Success: Retrieved list page {page_url}")

                title_el = page.query_selector("h1.title-1")
                if title_el and current_page == 1:
                    list_contents["list_name"] = title_el.inner_text().strip()

                desc_el = page.query_selector("div.body-text")
                if desc_el and current_page == 1:
                    list_contents["description"] = desc_el.inner_text().strip()

                posters = page.query_selector_all("li.poster-container")
                if not posters:
                    break

                for poster in posters:
                    film_div = poster.query_selector("div.film-poster")
                    if film_div:
                        film_data = {
                            "film_name": film_div.get_attribute("data-film-name"),
                            "film_slug": film_div.get_attribute("data-film-slug"),
                        }
                        img = poster.query_selector("img")
                        if img:
                            film_data["film_poster_image"] = img.get_attribute("src")
                        list_contents["films"].append(film_data)

                if not paginate:
                    break

                next_link = page.query_selector("a.next")
                if not next_link or current_page >= max_pages:
                    break
                current_page += 1

        except Exception as e:
            print(f"Error: Unable to process list page {current_page}: {e}")
        page.close()
        browser.close()

    return list_contents


def scrape_user_followers(target_url, paginate=True, max_pages=50):
    """
    scrapes user's followers list from letterboxd
    """
    base_followers_url = f"{target_url}followers/"
    followers_array = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        current_page = 1
        try:
            while True:
                if current_page == 1:
                    page_url = base_followers_url
                else:
                    page_url = f"{base_followers_url}page/{current_page}/"
                page.goto(page_url)
                print(f"Success: Retrieved followers page {page_url}")

                follower_items = page.query_selector_all("table.person-table tr")
                if not follower_items:
                    break

                for item in follower_items:
                    user_data = {
                        "username": None,
                        "display_name": None,
                        "profile_url": None,
                        "avatar_url": None,
                    }

                    avatar = item.query_selector("td.table-person a.avatar img")
                    if avatar:
                        user_data["avatar_url"] = avatar.get_attribute("src")

                    name_link = item.query_selector("td.table-person h3.title-3 a")
                    if name_link:
                        user_data["display_name"] = name_link.inner_text().strip()
                        user_data["profile_url"] = name_link.get_attribute("href")
                        if user_data["profile_url"]:
                            user_data["username"] = user_data["profile_url"].strip("/")

                    followers_array.append(user_data)

                if not paginate:
                    break

                next_link = page.query_selector("a.next")
                if not next_link or current_page >= max_pages:
                    break
                current_page += 1

        except Exception as e:
            print(f"Error: Unable to process followers page {current_page}: {e}")
        page.close()
        browser.close()

    return followers_array


def scrape_user_following(target_url, paginate=True, max_pages=50):
    """
    scrapes user's following list from letterboxd
    """
    base_following_url = f"{target_url}following/"
    following_array = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        current_page = 1
        try:
            while True:
                if current_page == 1:
                    page_url = base_following_url
                else:
                    page_url = f"{base_following_url}page/{current_page}/"
                page.goto(page_url)
                print(f"Success: Retrieved following page {page_url}")

                following_items = page.query_selector_all("table.person-table tr")
                if not following_items:
                    break

                for item in following_items:
                    user_data = {
                        "username": None,
                        "display_name": None,
                        "profile_url": None,
                        "avatar_url": None,
                    }

                    avatar = item.query_selector("td.table-person a.avatar img")
                    if avatar:
                        user_data["avatar_url"] = avatar.get_attribute("src")

                    name_link = item.query_selector("td.table-person h3.title-3 a")
                    if name_link:
                        user_data["display_name"] = name_link.inner_text().strip()
                        user_data["profile_url"] = name_link.get_attribute("href")
                        if user_data["profile_url"]:
                            user_data["username"] = user_data["profile_url"].strip("/")

                    following_array.append(user_data)

                if not paginate:
                    break

                next_link = page.query_selector("a.next")
                if not next_link or current_page >= max_pages:
                    break
                current_page += 1

        except Exception as e:
            print(f"Error: Unable to process following page {current_page}: {e}")
        page.close()
        browser.close()

    return following_array


def pretty_print_json(json_object):
    """
    pretty prints the json to
    the cli for easy viewing
    """
    print(json.dumps(json_object, indent=4))


def scrape_letterboxd_user_watchlist(target_url, paginate=True, max_pages=50):
    """
    scrapes a user's watchlist from letterboxd with pagination support
    """
    base_watchlist_url = f"{target_url}watchlist/"
    user_watchlist_array = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        current_page = 1
        try:
            while True:
                if current_page == 1:
                    page_url = base_watchlist_url
                else:
                    page_url = f"{base_watchlist_url}page/{current_page}/"
                page.goto(page_url)
                print(f"Success: Retrieved page URL {page_url}")

                poster_list = page.query_selector("ul.poster-list")
                if not poster_list:
                    break

                posters = poster_list.query_selector_all("li.poster-container")
                if not posters:
                    break

                for poster in posters:
                    film_name = poster.query_selector("div").get_attribute("data-film-name")
                    film_poster_image = poster.query_selector("div img").get_attribute("src")
                    user_watchlist_array.append(
                        {
                            "film_name": film_name,
                            "film_poster_image": film_poster_image,
                        }
                    )

                if not paginate:
                    break

                next_link = page.query_selector("a.next")
                if not next_link or current_page >= max_pages:
                    break
                current_page += 1

        except Exception as e:
            print(f"Error: Unable to process watchlist page {current_page}: {e}")
        page.close()
        browser.close()

    return user_watchlist_array


def scrape_letterboxd_user_films(target_url, paginate=True, max_pages=100):
    """
    scrapes all films a user has logged with pagination support
    """
    base_films_url = f"{target_url}films/"
    user_films_array = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        current_page = 1
        try:
            while True:
                if current_page == 1:
                    page_url = base_films_url
                else:
                    page_url = f"{base_films_url}page/{current_page}/"
                page.goto(page_url)
                print(f"Success: Retrieved films page URL {page_url}")

                poster_list = page.query_selector("ul.poster-list")
                if not poster_list:
                    break

                posters = poster_list.query_selector_all("li.poster-container")
                if not posters:
                    break

                for poster in posters:
                    film_div = poster.query_selector("div.film-poster")
                    if film_div:
                        film_name = film_div.get_attribute("data-film-name")
                        film_slug = film_div.get_attribute("data-film-slug")
                        img = poster.query_selector("div img")
                        film_poster_image = img.get_attribute("src") if img else None
                        user_films_array.append(
                            {
                                "film_name": film_name,
                                "film_slug": film_slug,
                                "film_poster_image": film_poster_image,
                            }
                        )

                if not paginate:
                    break

                next_link = page.query_selector("a.next")
                if not next_link or current_page >= max_pages:
                    break
                current_page += 1

        except Exception as e:
            print(f"Error: Unable to process films page {current_page}: {e}")
        page.close()
        browser.close()

    return user_films_array


def scrape_letterboxd_user(target_url):
    """
    scrapes user data from letterboxd
    """
    start_time = time.time()
    user_favourite_films_array = []
    user_recent_activity_array = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(target_url)
            print(f"Success: Retrieved page URL {target_url}")
            page.wait_for_selector("div#content div.content-wrap")
            main_div = page.query_selector("div#content div.content-wrap")

            user_profile = main_div.wait_for_selector(
                "section.profile-header.js-profile-header"
            )
            if user_profile:
                print("Success: User profile found!")
                user_data_person = user_profile.get_attribute("data-person")
                user_profile_image = user_profile.query_selector(
                    "div.profile-summary.js-profile-summary div.profile-avatar span img"
                ).get_attribute("src")
                user_name = user_profile.query_selector(
                    "div.profile-summary.js-profile-summary div.profile-name-and-actions.js-profile-name-and-actions h1.person-display-name span"
                ).inner_text()
                user_statistics_array = [
                    statistic.inner_text().strip()
                    for statistic in user_profile.query_selector_all(
                        "div.profile-summary.js-profile-summary div.profile-info.js-profile-info div.profile-stats.js-profile-stats h4.profile-statistic"
                    )
                ]
                user_bio = user_profile.query_selector(
                    "div.profile-summary.js-profile-summary div.profile-info.js-profile-info div.bio.js-bio div"
                ).inner_text()
                page.screenshot()
            else:
                print("Error: User profile not found!")

            user_favourite_films = main_div.wait_for_selector("section#favourites")
            if user_favourite_films:
                print("Success: User favourite films found!")
                for film in user_favourite_films.query_selector_all(
                    "ul.poster-list li.poster-container"
                ):
                    film_name = film.query_selector("div.film-poster").get_attribute(
                        "data-film-name"
                    )
                    film_poster_image = film.query_selector(
                        "div.film-poster div img"
                    ).get_attribute("src")
                    user_favourite_films_array.append(
                        {
                            "film_name": film_name,
                            "film_poster_image": film_poster_image,
                        }
                    )
            else:
                print("Error: User favourite films not found!")

            user_recent_activity = main_div.wait_for_selector("section#recent-activity")
            if user_recent_activity:
                print("Success: User recent activity found!")
                for film in user_recent_activity.query_selector_all(
                    "ul.poster-list li.poster-container"
                ):
                    film_name = film.query_selector("div.film-poster").get_attribute(
                        "data-film-name"
                    )
                    film_poster_image = film.query_selector(
                        "div.film-poster div img"
                    ).get_attribute("src")
                    user_recent_activity_array.append(
                        {
                            "film_name": film_name,
                            "film_poster_image": film_poster_image,
                        }
                    )
            else:
                print("Error: User recent activity not found!")

            user_data = {
                "metadata": {
                    "date_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "target_url": target_url,
                    "duration": time.strftime(
                        "%H:%M:%S", time.gmtime(time.time() - start_time)
                    ),
                },
                "scraped_data": {
                    "profile": {
                        "user_name": user_name,
                        "user_data_person": user_data_person,
                        "user_bio": user_bio,
                        "user_statistics": [
                            " ".join(el.split("\n")).lower()
                            for el in user_statistics_array
                        ],
                        "user_profile_image": user_profile_image,
                    },
                    "films": {
                        "favourite_films": user_favourite_films_array,
                        "recent_activity": user_recent_activity_array,
                        "watchlist": None,
                    },
                },
            }

        except Exception as e:
            print(f"Error: Unable to process {target_url}: {e}")
        page.close()
        browser.close()
    return user_data


def scrape_letterboxd(target_url, paginate=True):
    """
    wrapper function for user interfacing
    """
    buffer = scrape_letterboxd_user(target_url)
    watchlist = scrape_letterboxd_user_watchlist(target_url, paginate=paginate)
    all_films = scrape_letterboxd_user_films(target_url, paginate=paginate)
    if watchlist:
        buffer["scraped_data"]["films"]["watchlist"] = watchlist
    if all_films:
        buffer["scraped_data"]["films"]["all_films"] = all_films
    return buffer
