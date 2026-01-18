# ----- SCRAPING FUNCTIONS -----

import time
from playwright.sync_api import sync_playwright


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


def scrape_letterboxd_user_watchlist(target_url, paginate=True, max_pages=50):
    """
    scrapes a user's watchlist from letterboxd
    """
    base_watchlist_url = f"{target_url}watchlist/"
    watchlist_array = []
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
                print(f"Success: Retrieved watchlist page {page_url}")

                poster_containers = page.query_selector_all("ul.poster-list li.poster-container")
                if not poster_containers:
                    break

                for container in poster_containers:
                    film_poster = container.query_selector("div.film-poster")
                    if film_poster:
                        film_name = film_poster.get_attribute("data-film-name")
                        film_slug = film_poster.get_attribute("data-film-slug")
                        img = container.query_selector("div.film-poster div img")
                        film_poster_image = img.get_attribute("src") if img else None
                        watchlist_array.append(
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
            print(f"Error: Unable to process watchlist page {current_page}: {e}")
        page.close()
        browser.close()

    return watchlist_array


def scrape_letterboxd_user_films(target_url, paginate=True, max_pages=100):
    """
    scrapes all films watched by a user from letterboxd
    """
    base_films_url = f"{target_url}films/"
    films_array = []
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
                print(f"Success: Retrieved films page {page_url}")

                poster_containers = page.query_selector_all("ul.poster-list li.poster-container")
                if not poster_containers:
                    break

                for container in poster_containers:
                    film_poster = container.query_selector("div.film-poster")
                    if film_poster:
                        film_name = film_poster.get_attribute("data-film-name")
                        film_slug = film_poster.get_attribute("data-film-slug")
                        img = container.query_selector("div.film-poster div img")
                        film_poster_image = img.get_attribute("src") if img else None
                        films_array.append(
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

    return films_array


def scrape_letterboxd_user(target_url):
    """
    scrapes user profile data from letterboxd
    """
    user_data = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        start_time = time.time()
        try:
            page.goto(target_url)
            print(f"Success: Retrieved profile {target_url}")

            main_div = page.wait_for_selector("div#content div.content-wrap")
            if not main_div:
                print("Error: Main content not found!")
                return None

            user_profile_header = main_div.wait_for_selector(
                "section.profile-header.js-profile-header"
            )
            if not user_profile_header:
                print("Error: User profile header not found!")
                return None

            # extract profile image
            user_profile_image_el = page.query_selector(
                "div.profile-summary.js-profile-summary div.profile-avatar span img"
            )
            user_profile_image = (
                user_profile_image_el.get_attribute("src") if user_profile_image_el else None
            )

            # extract display name
            user_name_el = page.query_selector(
                "div.profile-summary.js-profile-summary div.profile-name-and-actions.js-profile-name-and-actions h1.person-display-name span"
            )
            user_name = user_name_el.inner_text().strip() if user_name_el else None

            # extract username from URL or data attribute
            user_data_person = target_url.rstrip("/").split("/")[-1]

            # extract bio
            user_bio_el = page.query_selector(
                "div.profile-summary.js-profile-summary div.profile-info.js-profile-info div.bio.js-bio div"
            )
            user_bio = user_bio_el.inner_text().strip() if user_bio_el else None

            # extract statistics
            user_statistics_array = []
            stat_elements = page.query_selector_all(
                "div.profile-summary.js-profile-summary div.profile-info.js-profile-info div.profile-stats.js-profile-stats h4.profile-statistic"
            )
            for stat in stat_elements:
                user_statistics_array.append(stat.inner_text().strip())

            # extract favourite films
            user_favourite_films_array = []
            user_favourites = main_div.query_selector("section#favourites")
            if user_favourites:
                print("Success: User favourite films found!")
                for film in user_favourites.query_selector_all(
                    "ul.poster-list li.poster-container"
                ):
                    film_poster = film.query_selector("div.film-poster")
                    if film_poster:
                        film_name = film_poster.get_attribute("data-film-name")
                        img = film.query_selector("div.film-poster div img")
                        film_poster_image = img.get_attribute("src") if img else None
                        user_favourite_films_array.append(
                            {
                                "film_name": film_name,
                                "film_poster_image": film_poster_image,
                            }
                        )
            else:
                print("Error: User favourite films not found!")

            # extract recent activity
            user_recent_activity_array = []
            user_recent_activity = main_div.query_selector("section#recent-activity")
            if user_recent_activity:
                print("Success: User recent activity found!")
                for film in user_recent_activity.query_selector_all(
                    "ul.poster-list li.poster-container"
                ):
                    film_poster = film.query_selector("div.film-poster")
                    if film_poster:
                        film_name = film_poster.get_attribute("data-film-name")
                        img = film.query_selector("div.film-poster div img")
                        film_poster_image = img.get_attribute("src") if img else None
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
