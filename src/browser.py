# ----- BROWSER POOL & RATE LIMITING -----

import time
import random


class BrowserPool:
    """
    manages a pool of browser instances for concurrent scraping
    """

    def __init__(self, pool_size=3, headless=True):
        """
        Args:
            pool_size: number of browser instances in pool
            headless: whether browsers run in headless mode
        """
        self.pool_size = pool_size
        self.headless = headless
        self._playwright = None
        self._browsers = []
        self._available = []
        self._in_use = set()

    def start(self):
        """initializes the browser pool"""
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        for _ in range(self.pool_size):
            browser = self._playwright.chromium.launch(headless=self.headless)
            self._browsers.append(browser)
            self._available.append(browser)
        print(f"Browser pool started with {self.pool_size} instances")

    def acquire(self):
        """acquires a browser from the pool, blocks if none available"""
        while not self._available:
            time.sleep(0.1)
        browser = self._available.pop()
        self._in_use.add(browser)
        return browser

    def release(self, browser):
        """returns a browser to the pool"""
        if browser in self._in_use:
            self._in_use.remove(browser)
            self._available.append(browser)

    def close(self):
        """closes all browsers and playwright"""
        for browser in self._browsers:
            try:
                browser.close()
            except Exception:
                pass
        if self._playwright:
            self._playwright.stop()
        self._browsers.clear()
        self._available.clear()
        self._in_use.clear()
        print("Browser pool closed")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


# global browser pool instance (initialized on demand)
_browser_pool = None


def get_browser_pool(pool_size=3, headless=True):
    """gets or creates the global browser pool"""
    global _browser_pool
    if _browser_pool is None:
        _browser_pool = BrowserPool(pool_size, headless)
        _browser_pool.start()
    return _browser_pool


def close_browser_pool():
    """closes the global browser pool"""
    global _browser_pool
    if _browser_pool:
        _browser_pool.close()
        _browser_pool = None


# ----- RATE LIMITING -----


class RateLimiter:
    """
    rate limiter with configurable delays between requests
    """

    def __init__(self, min_delay=1.0, max_delay=3.0, randomize=True):
        """
        Args:
            min_delay: minimum delay between requests in seconds
            max_delay: maximum delay for randomized delays
            randomize: if True, uses random delay between min and max
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.randomize = randomize
        self.last_request_time = 0

    def wait(self):
        """waits appropriate time before next request"""
        elapsed = time.time() - self.last_request_time
        if self.randomize:
            delay = random.uniform(self.min_delay, self.max_delay)
        else:
            delay = self.min_delay
        remaining = delay - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self.last_request_time = time.time()

    def reset(self):
        """resets the rate limiter"""
        self.last_request_time = 0


# global rate limiter instance with polite defaults
_rate_limiter = RateLimiter(min_delay=1.0, max_delay=2.0)


def set_rate_limit(min_delay=1.0, max_delay=2.0, randomize=True):
    """configures the global rate limiter"""
    global _rate_limiter
    _rate_limiter = RateLimiter(min_delay, max_delay, randomize)


def rate_limit_wait():
    """applies rate limiting delay before a request"""
    _rate_limiter.wait()


# ----- RETRY MECHANISM -----


def retry_with_backoff(
    func, max_retries=3, base_delay=1.0, max_delay=30.0, exceptions=(Exception,)
):
    """
    executes a function with exponential backoff retry logic

    Args:
        func: callable to execute
        max_retries: maximum number of retry attempts
        base_delay: initial delay in seconds
        max_delay: maximum delay between retries
        exceptions: tuple of exceptions to catch and retry

    Returns:
        result of func if successful, None if all retries fail
    """
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                delay = min(base_delay * (2**attempt), max_delay)
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed. Last error: {e}")
    return None


def make_request_with_retry(page, url, max_retries=3, base_delay=1.0):
    """
    navigates to a URL with retry logic for transient failures

    Args:
        page: playwright page object
        url: URL to navigate to
        max_retries: maximum retry attempts
        base_delay: initial backoff delay

    Returns:
        True if successful, False otherwise
    """
    for attempt in range(max_retries + 1):
        try:
            response = page.goto(url)
            if response and response.ok:
                return True
            if response and response.status >= 500:
                raise Exception(f"Server error: {response.status}")
            return True
        except Exception as e:
            if attempt < max_retries:
                delay = min(base_delay * (2**attempt), 30.0)
                print(
                    f"Request failed (attempt {attempt + 1}): {e}. Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
            else:
                print(f"Request failed after {max_retries + 1} attempts: {e}")
                return False
    return False
