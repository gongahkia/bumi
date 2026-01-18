# ----- PROGRESS TRACKING -----

import time


class ProgressTracker:
    """
    tracks progress of long-running scraping operations with callbacks
    """

    def __init__(self, total=0, callback=None):
        """
        Args:
            total: total number of items to process
            callback: function(current, total, message) called on updates
        """
        self.total = total
        self.current = 0
        self.callback = callback
        self.start_time = None
        self.errors = []

    def start(self, total=None):
        """starts tracking progress"""
        if total is not None:
            self.total = total
        self.current = 0
        self.start_time = time.time()
        self.errors = []
        self._notify(f"Starting operation with {self.total} items")

    def update(self, increment=1, message=None):
        """updates progress by increment"""
        self.current += increment
        msg = message or f"Processed {self.current}/{self.total}"
        self._notify(msg)

    def error(self, message):
        """records an error"""
        self.errors.append(message)
        self._notify(f"Error: {message}")

    def complete(self):
        """marks operation as complete"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        msg = f"Completed {self.current}/{self.total} in {elapsed:.1f}s"
        if self.errors:
            msg += f" ({len(self.errors)} errors)"
        self._notify(msg)

    def _notify(self, message):
        """calls the callback if set"""
        if self.callback:
            self.callback(self.current, self.total, message)
        else:
            print(f"[Progress] {message}")

    @property
    def percentage(self):
        """returns completion percentage"""
        if self.total == 0:
            return 0
        return (self.current / self.total) * 100

    @property
    def elapsed(self):
        """returns elapsed time in seconds"""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time


def create_progress_bar_callback():
    """creates a simple text-based progress bar callback"""

    def callback(current, total, message):
        if total > 0:
            pct = int((current / total) * 50)
            bar = "=" * pct + "-" * (50 - pct)
            print(f"\r[{bar}] {current}/{total} - {message}", end="", flush=True)
            if current >= total:
                print()
        else:
            print(f"\r{message}", end="", flush=True)

    return callback
