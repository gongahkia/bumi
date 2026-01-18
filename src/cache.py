# ----- CACHING SYSTEM -----

import time
import json
import hashlib
from pathlib import Path

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
