import logging
import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from scraper import fetch_codes
from notifier import send_code_notification
from database import init_db, get_seen_codes, mark_seen

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("yar-monitor")

URL = "https://codes.yar.gg/"
CHECK_INTERVAL = max(60, int(os.getenv("CHECK_INTERVAL_SECONDS", "300")))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()


def main():
    if not DISCORD_WEBHOOK_URL:
        raise SystemExit("Missing DISCORD_WEBHOOK_URL environment variable.")

    init_db()
    log.info("YAR giftcode monitor starting; interval=%s seconds", CHECK_INTERVAL)

    # Initial scan seeds the database and avoids announcing every existing code.
    first_run = not get_seen_codes()
    while True:
        try:
            codes = fetch_codes()
            seen = get_seen_codes()
            new_codes = [item for item in codes if item["code"] not in seen]

            if first_run:
                for item in codes:
                    mark_seen(item["code"], item)
                log.info("Initial scan: saved %d existing codes without notifications", len(codes))
                first_run = False
            else:
                for item in new_codes:
                    try:
                        send_code_notification(DISCORD_WEBHOOK_URL, item)
                        mark_seen(item["code"], item)
                        log.info("New code detected: %s", item["code"])
                    except Exception:
                        log.exception("Failed to notify about code %s; will retry next scan", item["code"])

            if not codes:
                log.warning("No codes extracted. The website may render data with JavaScript; inspect scraper.py output/logs.")
        except requests.RequestException:
            log.exception("Network error while checking codes.yar.gg")
        except Exception:
            log.exception("Unexpected error while checking codes.yar.gg")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
