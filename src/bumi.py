# ----- REQUIRED IMPORTS -----

import time
import json
from playwright.sync_api import sync_playwright

# ----- HELPER FUNCTIONS -----


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
