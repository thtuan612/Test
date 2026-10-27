# YAR Giftcode Monitor (Python)

A starter worker that checks `https://codes.yar.gg/` periodically and posts new code detections to a Discord webhook.

## Important limitation

The scraper is intentionally conservative and only parses server-rendered HTML. The website may render codes dynamically with JavaScript or expose data through a separate endpoint. In that case `scraper.py` needs a site-specific adapter. Reward information is currently `Chưa xác định` until the source data for rewards is confirmed. Do not assume this starter is already detecting every code correctly.

## Run locally

1. Install Python 3.11+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`, then set `DISCORD_WEBHOOK_URL`.
4. Start:
   ```bash
   python main.py
   ```

The first successful scan saves existing detections without notifying, to avoid flooding the channel. Later detections generate Discord embeds.

## Deploy to Railway

1. Push this folder to a new GitHub repository.
2. Create a Railway project from the repository.
3. Add the variable `DISCORD_WEBHOOK_URL` in Railway Variables.
4. Optionally set `CHECK_INTERVAL_SECONDS=300`.
5. For persistent SQLite state, attach a Railway Volume and set `DATABASE_PATH` to a file path inside its mount (for example `/data/giftcodes.sqlite3`).

## Validate the scraper

Run:
```bash
python -c "from scraper import fetch_codes; print(fetch_codes())"
```

If it returns an empty list, inspect the HTML/source data and update `scraper.py`. This can mean the website loads its data client-side; it does not necessarily mean there are no codes.
