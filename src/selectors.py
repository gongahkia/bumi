# ----- CSS SELECTOR CONFIGURATION -----

import json

DEFAULT_SELECTORS = {
    "profile": {
        "content_wrap": "div#content div.content-wrap",
        "header": "section.profile-header.js-profile-header",
        "avatar": "div.profile-summary.js-profile-summary div.profile-avatar span img",
        "display_name": "div.profile-summary.js-profile-summary div.profile-name-and-actions.js-profile-name-and-actions h1.person-display-name span",
        "statistics": "div.profile-summary.js-profile-summary div.profile-info.js-profile-info div.profile-stats.js-profile-stats h4.profile-statistic",
        "bio": "div.profile-summary.js-profile-summary div.profile-info.js-profile-info div.bio.js-bio div",
        "pro_badge": "span.badge.-pro",
        "patron_badge": "span.badge.-patron",
    },
    "films": {
        "favourites_section": "section#favourites",
        "activity_section": "section#recent-activity",
        "poster_list": "ul.poster-list",
        "poster_container": "li.poster-container",
        "film_poster": "div.film-poster",
        "poster_image": "div.film-poster div img",
    },
    "watchlist": {
        "poster_list": "ul.poster-list",
        "poster_container": "li.poster-container",
        "next_page": "a.next",
    },
    "film_page": {
        "header": "section.film-header-group",
        "title": "h1.headline-1",
        "year": "small.number a",
        "director": "span.directorlist a",
        "tagline": "h4.tagline",
        "description": "div.truncate p",
        "sidebar": "aside.sidebar",
        "runtime": "p.text-link",
        "genres": "div#tab-genres a.text-slug",
        "rating": "a.tooltip.display-rating",
    },
    "reviews": {
        "review_item": "li.film-detail",
        "rating": "span.rating",
        "body": "div.body-text",
        "date": "span.date a",
        "liked": "span.like.icon-liked",
    },
    "diary": {
        "entry_row": "tr.diary-entry-row",
        "film_details": "td.td-film-details div.film-poster",
        "calendar": "td.td-calendar a",
        "rating": "td.td-rating span.rating",
        "rewatch": "td.td-rewatch span.icon-status-rewatch",
        "like": "td.td-like span.icon-liked",
        "review_icon": "td.td-review a.icon-review",
    },
    "lists": {
        "list_item": "section.list-set",
        "title": "h2.title a",
        "description": "div.body-text p",
        "count": "small.value",
    },
    "social": {
        "person_table": "table.person-table tr",
        "avatar": "td.table-person a.avatar img",
        "name_link": "td.table-person h3.title-3 a",
    },
}

_selectors = DEFAULT_SELECTORS.copy()


def load_selectors_from_file(filepath):
    """
    loads CSS selectors from external JSON config file

    Args:
        filepath: path to JSON config file

    Returns:
        loaded selectors dict
    """
    global _selectors
    with open(filepath, "r", encoding="utf-8") as f:
        custom_selectors = json.load(f)

    # deep merge with defaults
    for category, selectors in custom_selectors.items():
        if category not in _selectors:
            _selectors[category] = {}
        _selectors[category].update(selectors)

    print(f"Loaded selectors from {filepath}")
    return _selectors


def save_selectors_to_file(filepath):
    """
    saves current selectors to JSON config file

    Args:
        filepath: path to save config file
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(_selectors, f, indent=2)
    print(f"Saved selectors to {filepath}")


def get_selector(category, name):
    """
    gets a CSS selector by category and name

    Args:
        category: selector category (e.g., 'profile', 'films')
        name: selector name within category

    Returns:
        CSS selector string or None
    """
    return _selectors.get(category, {}).get(name)


def set_selector(category, name, selector):
    """
    sets a CSS selector

    Args:
        category: selector category
        name: selector name
        selector: CSS selector string
    """
    if category not in _selectors:
        _selectors[category] = {}
    _selectors[category][name] = selector


def reset_selectors():
    """resets selectors to defaults"""
    global _selectors
    _selectors = DEFAULT_SELECTORS.copy()
