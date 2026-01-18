# ----- TIMEOUT CONFIGURATION -----


class TimeoutConfig:
    """
    configurable timeout settings for scraping operations
    """

    def __init__(
        self,
        page_load_timeout=30000,
        element_wait_timeout=10000,
        navigation_timeout=30000,
        script_timeout=30000,
    ):
        """
        Args:
            page_load_timeout: timeout for page load in milliseconds
            element_wait_timeout: timeout for element waits in milliseconds
            navigation_timeout: timeout for navigation in milliseconds
            script_timeout: timeout for script execution in milliseconds
        """
        self.page_load_timeout = page_load_timeout
        self.element_wait_timeout = element_wait_timeout
        self.navigation_timeout = navigation_timeout
        self.script_timeout = script_timeout


# global timeout configuration
_timeout_config = TimeoutConfig()


def set_timeouts(page_load=30000, element_wait=10000, navigation=30000, script=30000):
    """configures global timeout settings"""
    global _timeout_config
    _timeout_config = TimeoutConfig(page_load, element_wait, navigation, script)


def get_timeout_config():
    """returns current timeout configuration"""
    return _timeout_config


def apply_timeouts_to_page(page):
    """applies timeout configuration to a playwright page"""
    config = get_timeout_config()
    page.set_default_timeout(config.element_wait_timeout)
    page.set_default_navigation_timeout(config.navigation_timeout)


def safe_goto(page, url, timeout=None):
    """
    navigates to URL with timeout handling

    Args:
        page: playwright page object
        url: URL to navigate to
        timeout: optional timeout override in milliseconds

    Returns:
        response object if successful, None on timeout
    """
    config = get_timeout_config()
    effective_timeout = timeout or config.page_load_timeout
    try:
        response = page.goto(url, timeout=effective_timeout)
        return response
    except Exception as e:
        if "timeout" in str(e).lower():
            print(f"Timeout loading {url} after {effective_timeout}ms")
        else:
            print(f"Error loading {url}: {e}")
        return None


def safe_wait_for_selector(page, selector, timeout=None):
    """
    waits for element with timeout handling

    Args:
        page: playwright page object
        selector: CSS selector to wait for
        timeout: optional timeout override in milliseconds

    Returns:
        element if found, None on timeout
    """
    config = get_timeout_config()
    effective_timeout = timeout or config.element_wait_timeout
    try:
        return page.wait_for_selector(selector, timeout=effective_timeout)
    except Exception as e:
        if "timeout" in str(e).lower():
            print(f"Timeout waiting for {selector} after {effective_timeout}ms")
        return None
