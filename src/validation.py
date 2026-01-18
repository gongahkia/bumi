# ----- INPUT VALIDATION -----

import re
import urllib.parse
from playwright.sync_api import sync_playwright

from .exceptions import InvalidURLError

LETTERBOXD_DOMAIN = "letterboxd.com"
LETTERBOXD_URL_PATTERN = re.compile(
    r"^https?://(?:www\.)?letterboxd\.com/([a-zA-Z0-9_]+)/?$"
)
LETTERBOXD_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


def validate_letterboxd_url(url):
    """
    validates a letterboxd profile URL

    Args:
        url: URL to validate

    Returns:
        dict with 'valid', 'username', and 'error' keys

    Raises:
        InvalidURLError: if URL is invalid
    """
    result = {"valid": False, "username": None, "error": None}

    if not url:
        result["error"] = "URL cannot be empty"
        return result

    # normalize URL
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # parse URL
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as e:
        result["error"] = f"Failed to parse URL: {e}"
        return result

    # check domain
    domain = parsed.netloc.lower().replace("www.", "")
    if domain != LETTERBOXD_DOMAIN:
        result["error"] = f"Not a Letterboxd URL (domain: {domain})"
        return result

    # extract username from path
    path = parsed.path.strip("/")
    path_parts = path.split("/")

    if not path_parts or not path_parts[0]:
        result["error"] = "No username found in URL"
        return result

    username = path_parts[0]

    # validate username format
    if not LETTERBOXD_USERNAME_PATTERN.match(username):
        result["error"] = f"Invalid username format: {username}"
        return result

    result["valid"] = True
    result["username"] = username
    return result


def validate_username(username):
    """
    validates a letterboxd username

    Args:
        username: username to validate

    Returns:
        dict with 'valid' and 'error' keys
    """
    result = {"valid": False, "error": None}

    if not username:
        result["error"] = "Username cannot be empty"
        return result

    username = username.strip()

    if len(username) < 2:
        result["error"] = "Username too short (min 2 characters)"
        return result

    if len(username) > 30:
        result["error"] = "Username too long (max 30 characters)"
        return result

    if not LETTERBOXD_USERNAME_PATTERN.match(username):
        result["error"] = "Username can only contain letters, numbers, and underscores"
        return result

    result["valid"] = True
    return result


def check_profile_exists(target_url):
    """
    checks if a letterboxd profile exists and is accessible

    Args:
        target_url: full URL to profile

    Returns:
        dict with 'exists', 'status', and 'error' keys
    """
    result = {"exists": False, "status": None, "error": None}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            response = page.goto(target_url, timeout=15000)
            result["status"] = response.status if response else None

            if response and response.status == 200:
                # check for profile header to confirm it's a real profile
                profile_header = page.query_selector("section.profile-header")
                if profile_header:
                    result["exists"] = True
                else:
                    result["error"] = "Page loaded but no profile found"
            elif response and response.status == 404:
                result["error"] = "Profile not found (404)"
            elif response and response.status == 429:
                result["error"] = "Rate limited (429)"
            else:
                result["error"] = (
                    f"Unexpected status: {response.status if response else 'no response'}"
                )

        except Exception as e:
            result["error"] = str(e)
        page.close()
        browser.close()

    return result


def normalize_profile_url(input_str):
    """
    normalizes a username or URL to a standard profile URL

    Args:
        input_str: username or URL

    Returns:
        normalized profile URL
    """
    input_str = input_str.strip()

    # if it's already a full URL
    if input_str.startswith(("http://", "https://")):
        validation = validate_letterboxd_url(input_str)
        if validation["valid"]:
            return f"https://letterboxd.com/{validation['username']}/"
        raise InvalidURLError(input_str, validation["error"])

    # if it's just a username
    validation = validate_username(input_str)
    if validation["valid"]:
        return f"https://letterboxd.com/{input_str}/"
    raise InvalidURLError(input_str, validation["error"])
