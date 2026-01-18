# ----- USER COMPARISON -----

from .scrapers import scrape_letterboxd_user_films


def compare_users(username1, username2, paginate=True):
    """
    compares two users' watched films to find common and unique films

    Args:
        username1: first letterboxd username
        username2: second letterboxd username
        paginate: whether to paginate through all films

    Returns:
        dict with common_films, unique_to_user1, unique_to_user2, and statistics
    """
    url1 = f"https://letterboxd.com/{username1}/"
    url2 = f"https://letterboxd.com/{username2}/"

    print(f"Fetching films for {username1}...")
    films1 = scrape_letterboxd_user_films(url1, paginate=paginate)

    print(f"Fetching films for {username2}...")
    films2 = scrape_letterboxd_user_films(url2, paginate=paginate)

    # Create sets of film slugs for comparison
    slugs1 = {f["film_slug"] for f in films1 if f.get("film_slug")}
    slugs2 = {f["film_slug"] for f in films2 if f.get("film_slug")}

    # Find common and unique
    common_slugs = slugs1 & slugs2
    unique_to_1 = slugs1 - slugs2
    unique_to_2 = slugs2 - slugs1

    # Build film lookup for details
    film_lookup1 = {f["film_slug"]: f for f in films1 if f.get("film_slug")}
    film_lookup2 = {f["film_slug"]: f for f in films2 if f.get("film_slug")}

    # Get full film data for each category
    common_films = [film_lookup1.get(s) or film_lookup2.get(s) for s in common_slugs]
    unique_films_1 = [film_lookup1[s] for s in unique_to_1]
    unique_films_2 = [film_lookup2[s] for s in unique_to_2]

    # Calculate compatibility score
    total_unique = len(slugs1 | slugs2)
    compatibility = (len(common_slugs) / total_unique * 100) if total_unique > 0 else 0

    return {
        "user1": username1,
        "user2": username2,
        "statistics": {
            "user1_total_films": len(slugs1),
            "user2_total_films": len(slugs2),
            "common_count": len(common_slugs),
            "unique_to_user1_count": len(unique_to_1),
            "unique_to_user2_count": len(unique_to_2),
            "compatibility_percentage": round(compatibility, 2),
        },
        "common_films": common_films,
        "unique_to_user1": unique_films_1,
        "unique_to_user2": unique_films_2,
    }


def find_watch_recommendations(username1, username2, paginate=True):
    """
    finds films that one user has watched that the other hasn't (recommendations)

    Args:
        username1: user to get recommendations for
        username2: user whose films to recommend from

    Returns:
        list of films user2 has watched that user1 hasn't
    """
    comparison = compare_users(username1, username2, paginate=paginate)
    return {
        "recommendations_for": username1,
        "based_on": username2,
        "films": comparison["unique_to_user2"],
        "count": comparison["statistics"]["unique_to_user2_count"],
    }
