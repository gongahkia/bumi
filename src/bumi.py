# Bumi - Letterboxd Profile Scraper
# Main entry point - re-exports all functionality from submodules for backward compatibility

# ----- REQUIRED IMPORTS -----

import os
import time
import json
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright

# Re-export everything from submodules for backward compatibility
from .exceptions import (
    BumiException,
    ProfileNotFoundError,
    RateLimitedError,
    NetworkError,
    TimeoutError,
    ParseError,
    InvalidURLError,
    FilmNotFoundError,
    ListNotFoundError,
    StorageError,
    ConfigurationError,
)

from .validation import (
    validate_letterboxd_url,
    validate_username,
    check_profile_exists,
    normalize_profile_url,
    LETTERBOXD_DOMAIN,
    LETTERBOXD_URL_PATTERN,
    LETTERBOXD_USERNAME_PATTERN,
)

from .selectors import (
    DEFAULT_SELECTORS,
    load_selectors_from_file,
    save_selectors_to_file,
    get_selector,
    set_selector,
    reset_selectors,
    _selectors,
)

from .cache import (
    cache_get,
    cache_set,
    cache_clear,
    cache_clear_expired,
    CACHE_DIR,
    DEFAULT_TTL,
    _get_cache_path,
)

from .progress import (
    ProgressTracker,
    create_progress_bar_callback,
)

from .config import (
    TimeoutConfig,
    set_timeouts,
    get_timeout_config,
    apply_timeouts_to_page,
    safe_goto,
    safe_wait_for_selector,
)

from .browser import (
    BrowserPool,
    get_browser_pool,
    close_browser_pool,
    RateLimiter,
    set_rate_limit,
    rate_limit_wait,
    retry_with_backoff,
    make_request_with_retry,
)

from .parsers import (
    parse_statistic_value,
    parse_user_statistics,
    parse_rating_string,
    parse_runtime_string,
    extract_bio_links,
)

from .export import (
    export_to_csv,
    export_to_xml,
    export_to_json,
    export_data,
    pretty_print_json,
)

from .storage import (
    SQLiteStorage,
    PostgreSQLStorage,
)

from .snapshot import (
    batch_scrape_users,
    aggregate_batch_results,
    compute_delta,
    detect_profile_changes,
    save_snapshot,
    load_latest_snapshot,
)

from .scrapers import (
    scrape_film_details,
    scrape_user_reviews,
    scrape_user_diary,
    scrape_user_lists,
    scrape_list_contents,
    scrape_user_followers,
    scrape_user_following,
    scrape_letterboxd_user_watchlist,
    scrape_letterboxd_user_films,
    scrape_letterboxd_user,
    scrape_letterboxd,
)

from .api import (
    create_api_server,
    run_api_server,
)

from .webhooks import (
    WebhookManager,
    register_webhook,
    unregister_webhook,
    notify_webhook,
    get_webhook_manager,
    scrape_with_webhook,
)

from .search import (
    search_films,
    search_films_advanced,
    get_popular_films,
    scrape_activity_feed,
    scrape_popular_reviews,
)

__version__ = "1.0.0"
