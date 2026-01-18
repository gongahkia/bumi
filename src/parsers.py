# ----- STATISTICS PARSING -----

import re
from playwright.sync_api import sync_playwright


def parse_statistic_value(stat_string):
    """
    parses a statistic string into numeric value and label

    Args:
        stat_string: string like "1,234 films" or "523 following"

    Returns:
        dict with 'value' (int), 'label' (str), 'raw' (str)
    """
    stat_string = stat_string.strip().lower()
    result = {"value": None, "label": None, "raw": stat_string}

    # match number with optional commas followed by label
    match = re.match(r"([\d,]+)\s*(\w+)", stat_string)
    if match:
        num_str = match.group(1).replace(",", "")
        result["value"] = int(num_str)
        result["label"] = match.group(2)
    return result


def parse_user_statistics(stats_array):
    """
    parses array of user statistics into structured format

    Args:
        stats_array: list of strings like ["1,234 films", "523 following"]

    Returns:
        dict with parsed statistics including:
        - films_watched: int
        - films_this_year: int
        - lists: int
        - following: int
        - followers: int
        - raw: original array
    """
    result = {
        "films_watched": None,
        "films_this_year": None,
        "lists": None,
        "following": None,
        "followers": None,
        "raw": stats_array,
    }

    for stat in stats_array:
        parsed = parse_statistic_value(stat)
        if parsed["value"] is None:
            continue

        label = parsed["label"]
        value = parsed["value"]

        if label in ("films", "film"):
            result["films_watched"] = value
        elif label == "year" or "this year" in stat.lower():
            result["films_this_year"] = value
        elif label in ("lists", "list"):
            result["lists"] = value
        elif label == "following":
            result["following"] = value
        elif label in ("followers", "follower"):
            result["followers"] = value

    return result


def parse_rating_string(rating_str):
    """
    parses a rating string into numeric value

    Args:
        rating_str: star rating like "★★★★" or "★★★½"

    Returns:
        float rating value (0.5 to 5.0) or None
    """
    if not rating_str:
        return None

    full_stars = rating_str.count("★")
    half_stars = rating_str.count("½")
    return full_stars + (0.5 * half_stars) if (full_stars or half_stars) else None


def parse_runtime_string(runtime_str):
    """
    parses a runtime string into minutes

    Args:
        runtime_str: string like "142 mins" or "2h 22m"

    Returns:
        int minutes or None
    """
    if not runtime_str:
        return None

    runtime_str = runtime_str.lower().strip()

    # try "X mins" format
    match = re.search(r"(\d+)\s*mins?", runtime_str)
    if match:
        return int(match.group(1))

    # try "Xh Ym" format
    hours_match = re.search(r"(\d+)\s*h", runtime_str)
    mins_match = re.search(r"(\d+)\s*m", runtime_str)
    total = 0
    if hours_match:
        total += int(hours_match.group(1)) * 60
    if mins_match:
        total += int(mins_match.group(1))
    return total if total > 0 else None


def extract_bio_links(target_url):
    """
    extracts links and social media accounts from user bio

    Args:
        target_url: letterboxd user profile URL

    Returns:
        dict with extracted links and social accounts
    """
    result = {
        "website": None,
        "twitter": None,
        "instagram": None,
        "letterboxd_pro": False,
        "letterboxd_patron": False,
        "bio_links": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(target_url)
            print(f"Success: Retrieved profile for bio links {target_url}")

            # check for pro/patron badges
            pro_badge = page.query_selector("span.badge.-pro")
            if pro_badge:
                result["letterboxd_pro"] = True
            patron_badge = page.query_selector("span.badge.-patron")
            if patron_badge:
                result["letterboxd_patron"] = True

            # extract website link
            website_link = page.query_selector("a.icon-website")
            if website_link:
                result["website"] = website_link.get_attribute("href")

            # extract twitter link
            twitter_link = page.query_selector("a.icon-twitter")
            if twitter_link:
                href = twitter_link.get_attribute("href")
                result["twitter"] = href
                # extract username from URL
                match = re.search(r"twitter\.com/(\w+)", href)
                if match:
                    result["twitter_username"] = match.group(1)

            # extract all links from bio text
            bio_section = page.query_selector("div.bio.js-bio")
            if bio_section:
                links = bio_section.query_selector_all("a")
                for link in links:
                    href = link.get_attribute("href")
                    text = link.inner_text().strip()
                    if href:
                        link_data = {"url": href, "text": text}
                        result["bio_links"].append(link_data)

                        # detect instagram
                        if "instagram.com" in href.lower():
                            result["instagram"] = href
                            match = re.search(r"instagram\.com/(\w+)", href)
                            if match:
                                result["instagram_username"] = match.group(1)

        except Exception as e:
            print(f"Error extracting bio links: {e}")
        page.close()
        browser.close()

    return result
