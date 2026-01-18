# ----- BATCH OPERATIONS & SNAPSHOTS -----

import time
import json
from pathlib import Path

from .progress import ProgressTracker


def batch_scrape_users(usernames, base_url="https://letterboxd.com", progress_callback=None):
    """
    scrapes multiple user profiles

    Args:
        usernames: list of usernames to scrape
        base_url: base letterboxd URL
        progress_callback: optional progress callback

    Returns:
        dict with results for each user
    """
    from .scrapers import scrape_letterboxd

    tracker = ProgressTracker(len(usernames), progress_callback)
    tracker.start()
    results = {}

    for username in usernames:
        try:
            target_url = f"{base_url}/{username}/"
            result = scrape_letterboxd(target_url, paginate=True)
            results[username] = {"success": True, "data": result}
            tracker.update(message=f"Scraped {username}")
        except Exception as e:
            results[username] = {"success": False, "error": str(e)}
            tracker.error(f"Failed to scrape {username}: {e}")

    tracker.complete()
    return results


def aggregate_batch_results(batch_results):
    """
    aggregates batch scrape results into summary statistics

    Args:
        batch_results: dict of results from batch_scrape_users

    Returns:
        dict with aggregated statistics
    """
    stats = {
        "total_users": len(batch_results),
        "successful": 0,
        "failed": 0,
        "total_films_watched": 0,
        "total_watchlist_items": 0,
        "users": [],
    }

    for username, result in batch_results.items():
        if result.get("success"):
            stats["successful"] += 1
            data = result.get("data", {})
            scraped = data.get("scraped_data", {})

            # extract film counts
            profile = scraped.get("profile", {})
            stats_raw = profile.get("user_statistics", [])
            for stat in stats_raw:
                if "films" in stat.lower():
                    try:
                        count = int("".join(filter(str.isdigit, stat.split()[0])))
                        stats["total_films_watched"] += count
                    except (ValueError, IndexError):
                        pass

            # count watchlist
            watchlist = scraped.get("films", {}).get("watchlist", [])
            if watchlist:
                stats["total_watchlist_items"] += len(watchlist)

            stats["users"].append(
                {
                    "username": username,
                    "display_name": profile.get("user_name"),
                }
            )
        else:
            stats["failed"] += 1

    return stats


def compute_delta(old_data, new_data, path=""):
    """
    computes differences between two data snapshots

    Args:
        old_data: previous data
        new_data: current data
        path: current path in nested structure

    Returns:
        dict with added, removed, and changed items
    """
    delta = {"added": [], "removed": [], "changed": []}

    if isinstance(old_data, dict) and isinstance(new_data, dict):
        old_keys = set(old_data.keys())
        new_keys = set(new_data.keys())

        # added keys
        for key in new_keys - old_keys:
            delta["added"].append({"path": f"{path}.{key}" if path else key, "value": new_data[key]})

        # removed keys
        for key in old_keys - new_keys:
            delta["removed"].append({"path": f"{path}.{key}" if path else key, "value": old_data[key]})

        # changed keys
        for key in old_keys & new_keys:
            new_path = f"{path}.{key}" if path else key
            if old_data[key] != new_data[key]:
                if isinstance(old_data[key], (dict, list)) and isinstance(new_data[key], (dict, list)):
                    sub_delta = compute_delta(old_data[key], new_data[key], new_path)
                    delta["added"].extend(sub_delta["added"])
                    delta["removed"].extend(sub_delta["removed"])
                    delta["changed"].extend(sub_delta["changed"])
                else:
                    delta["changed"].append(
                        {
                            "path": new_path,
                            "old_value": old_data[key],
                            "new_value": new_data[key],
                        }
                    )

    elif isinstance(old_data, list) and isinstance(new_data, list):
        old_set = set(str(x) for x in old_data)
        new_set = set(str(x) for x in new_data)

        for item in new_set - old_set:
            delta["added"].append({"path": path, "value": item})
        for item in old_set - new_set:
            delta["removed"].append({"path": path, "value": item})

    else:
        if old_data != new_data:
            delta["changed"].append(
                {"path": path, "old_value": old_data, "new_value": new_data}
            )

    return delta


def detect_profile_changes(old_profile, new_profile):
    """
    detects meaningful changes between profile snapshots

    Args:
        old_profile: previous profile data
        new_profile: current profile data

    Returns:
        dict summarizing profile changes
    """
    delta = compute_delta(old_profile, new_profile)

    summary = {
        "has_changes": bool(delta["added"] or delta["removed"] or delta["changed"]),
        "total_changes": len(delta["added"]) + len(delta["removed"]) + len(delta["changed"]),
        "delta": delta,
    }

    # categorize changes
    summary["watchlist_changes"] = [
        c
        for c in delta["added"] + delta["removed"]
        if "watchlist" in c.get("path", "")
    ]
    summary["favourite_changes"] = [
        c
        for c in delta["added"] + delta["removed"]
        if "favourite" in c.get("path", "")
    ]
    summary["profile_changes"] = [
        c for c in delta["changed"] if "profile" in c.get("path", "")
    ]

    return summary


def save_snapshot(data, username, snapshot_dir=None):
    """
    saves a snapshot of scrape data for later comparison

    Args:
        data: scrape data to save
        username: letterboxd username
        snapshot_dir: directory for snapshots (default: ~/.bumi_snapshots)

    Returns:
        path to saved snapshot
    """
    if snapshot_dir is None:
        snapshot_dir = Path.home() / ".bumi_snapshots"
    snapshot_dir = Path(snapshot_dir)
    snapshot_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{username}_{timestamp}.json"
    filepath = snapshot_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return str(filepath)


def load_latest_snapshot(username, snapshot_dir=None):
    """
    loads the most recent snapshot for a user

    Args:
        username: letterboxd username
        snapshot_dir: directory for snapshots

    Returns:
        tuple of (data, filepath) or (None, None) if no snapshot
    """
    if snapshot_dir is None:
        snapshot_dir = Path.home() / ".bumi_snapshots"
    snapshot_dir = Path(snapshot_dir)

    if not snapshot_dir.exists():
        return None, None

    snapshots = sorted(snapshot_dir.glob(f"{username}_*.json"), reverse=True)
    if not snapshots:
        return None, None

    latest = snapshots[0]
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data, str(latest)
