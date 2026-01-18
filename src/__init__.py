# Bumi - Letterboxd Profile Scraper
# Re-export all public APIs for convenience

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
)

from .selectors import (
    DEFAULT_SELECTORS,
    load_selectors_from_file,
    save_selectors_to_file,
    get_selector,
    set_selector,
    reset_selectors,
)

from .cache import (
    cache_get,
    cache_set,
    cache_clear,
    cache_clear_expired,
    CACHE_DIR,
    DEFAULT_TTL,
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

from .comparison import (
    compare_users,
    find_watch_recommendations,
)

__version__ = "1.0.0"
__all__ = [
    # Exceptions
    "BumiException",
    "ProfileNotFoundError",
    "RateLimitedError",
    "NetworkError",
    "TimeoutError",
    "ParseError",
    "InvalidURLError",
    "FilmNotFoundError",
    "ListNotFoundError",
    "StorageError",
    "ConfigurationError",
    # Validation
    "validate_letterboxd_url",
    "validate_username",
    "check_profile_exists",
    "normalize_profile_url",
    "LETTERBOXD_DOMAIN",
    # Selectors
    "DEFAULT_SELECTORS",
    "load_selectors_from_file",
    "save_selectors_to_file",
    "get_selector",
    "set_selector",
    "reset_selectors",
    # Cache
    "cache_get",
    "cache_set",
    "cache_clear",
    "cache_clear_expired",
    "CACHE_DIR",
    "DEFAULT_TTL",
    # Progress
    "ProgressTracker",
    "create_progress_bar_callback",
    # Config
    "TimeoutConfig",
    "set_timeouts",
    "get_timeout_config",
    "apply_timeouts_to_page",
    "safe_goto",
    "safe_wait_for_selector",
    # Browser
    "BrowserPool",
    "get_browser_pool",
    "close_browser_pool",
    "RateLimiter",
    "set_rate_limit",
    "rate_limit_wait",
    "retry_with_backoff",
    "make_request_with_retry",
    # Parsers
    "parse_statistic_value",
    "parse_user_statistics",
    "parse_rating_string",
    "parse_runtime_string",
    "extract_bio_links",
    # Export
    "export_to_csv",
    "export_to_xml",
    "export_to_json",
    "export_data",
    "pretty_print_json",
    # Storage
    "SQLiteStorage",
    "PostgreSQLStorage",
    # Snapshot
    "batch_scrape_users",
    "aggregate_batch_results",
    "compute_delta",
    "detect_profile_changes",
    "save_snapshot",
    "load_latest_snapshot",
    # Scrapers
    "scrape_film_details",
    "scrape_user_reviews",
    "scrape_user_diary",
    "scrape_user_lists",
    "scrape_list_contents",
    "scrape_user_followers",
    "scrape_user_following",
    "scrape_letterboxd_user_watchlist",
    "scrape_letterboxd_user_films",
    "scrape_letterboxd_user",
    "scrape_letterboxd",
    # API
    "create_api_server",
    "run_api_server",
    # Webhooks
    "WebhookManager",
    "register_webhook",
    "unregister_webhook",
    "notify_webhook",
    "get_webhook_manager",
    "scrape_with_webhook",
    # Search
    "search_films",
    "search_films_advanced",
    "get_popular_films",
    "scrape_activity_feed",
    "scrape_popular_reviews",
    # Comparison
    "compare_users",
    "find_watch_recommendations",
]
