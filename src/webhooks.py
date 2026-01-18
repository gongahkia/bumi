# ----- WEBHOOK NOTIFICATIONS -----

import time
import json
import threading
from urllib.request import urlopen, Request
from urllib.error import URLError

from .scrapers import scrape_letterboxd


class WebhookManager:
    """
    manages webhook notifications for scrape job completions
    """

    def __init__(self):
        self.webhooks = {}
        self._lock = threading.Lock()

    def register(self, webhook_id, url, events=None, headers=None):
        """
        registers a webhook

        Args:
            webhook_id: unique identifier for webhook
            url: URL to POST notifications to
            events: list of event types to notify (default: all)
            headers: optional headers to include in requests
        """
        with self._lock:
            self.webhooks[webhook_id] = {
                "url": url,
                "events": events or ["scrape_complete", "scrape_error", "batch_complete"],
                "headers": headers or {},
                "active": True,
            }
        return webhook_id

    def unregister(self, webhook_id):
        """removes a webhook"""
        with self._lock:
            if webhook_id in self.webhooks:
                del self.webhooks[webhook_id]
                return True
        return False

    def notify(self, event_type, data, async_send=True):
        """
        sends notification to all registered webhooks

        Args:
            event_type: type of event
            data: event data to send
            async_send: whether to send asynchronously
        """
        payload = {
            "event": event_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": data,
        }

        with self._lock:
            targets = [
                (wid, wh)
                for wid, wh in self.webhooks.items()
                if wh["active"] and event_type in wh.get("events", [])
            ]

        for webhook_id, webhook in targets:
            if async_send:
                thread = threading.Thread(
                    target=self._send_notification, args=(webhook_id, webhook, payload)
                )
                thread.daemon = True
                thread.start()
            else:
                self._send_notification(webhook_id, webhook, payload)

    def _send_notification(self, webhook_id, webhook, payload):
        """sends a single notification"""
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Bumi-Webhook/1.0",
            }
            headers.update(webhook.get("headers", {}))

            json_data = json.dumps(payload).encode("utf-8")
            request = Request(
                webhook["url"], data=json_data, headers=headers, method="POST"
            )

            with urlopen(request, timeout=30) as response:
                print(
                    f"Webhook {webhook_id}: sent to {webhook['url']}, status {response.status}"
                )

        except URLError as e:
            print(f"Webhook {webhook_id}: failed to send to {webhook['url']}: {e}")
        except Exception as e:
            print(f"Webhook {webhook_id}: error: {e}")

    def list_webhooks(self):
        """returns list of registered webhooks"""
        with self._lock:
            return {
                wid: {"url": wh["url"], "events": wh["events"], "active": wh["active"]}
                for wid, wh in self.webhooks.items()
            }


# global webhook manager instance
_webhook_manager = WebhookManager()


def register_webhook(url, events=None, webhook_id=None, headers=None):
    """
    registers a webhook for notifications

    Args:
        url: URL to POST notifications to
        events: list of event types (default: all)
        webhook_id: optional custom ID
        headers: optional headers

    Returns:
        webhook ID
    """
    wid = webhook_id or f"webhook_{int(time.time() * 1000)}"
    return _webhook_manager.register(wid, url, events, headers)


def unregister_webhook(webhook_id):
    """removes a webhook"""
    return _webhook_manager.unregister(webhook_id)


def notify_webhook(event_type, data):
    """sends a webhook notification"""
    _webhook_manager.notify(event_type, data)


def get_webhook_manager():
    """returns the global webhook manager"""
    return _webhook_manager


def scrape_with_webhook(target_url, webhook_url=None, paginate=True):
    """
    scrapes a profile and sends webhook notification on completion

    Args:
        target_url: letterboxd profile URL
        webhook_url: optional webhook URL for this job only
        paginate: whether to paginate

    Returns:
        scrape result
    """
    job_id = f"job_{int(time.time() * 1000)}"

    try:
        result = scrape_letterboxd(target_url, paginate=paginate)
        notify_webhook(
            "scrape_complete",
            {
                "job_id": job_id,
                "target_url": target_url,
                "success": True,
                "result": result,
            },
        )

        if webhook_url:
            temp_id = register_webhook(webhook_url, ["scrape_complete"])
            notify_webhook(
                "scrape_complete",
                {
                    "job_id": job_id,
                    "target_url": target_url,
                    "success": True,
                },
            )
            unregister_webhook(temp_id)

        return result

    except Exception as e:
        notify_webhook(
            "scrape_error",
            {
                "job_id": job_id,
                "target_url": target_url,
                "success": False,
                "error": str(e),
            },
        )
        raise
