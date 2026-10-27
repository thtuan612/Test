"""HTML scraper for codes.yar.gg.

This first version extracts code-like strings from server-rendered HTML. If the site
renders its list entirely with JavaScript, this will need a site-specific API/browser
adapter. It deliberately does not guess an undocumented API endpoint.
"""
import re
import requests
from bs4 import BeautifulSoup

URL = "https://codes.yar.gg/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; YARGiftcodeMonitor/1.0; +https://codes.yar.gg/)"
}

# Conservative candidate pattern: alphanumeric codes containing at least one digit,
# with a reasonable length. Tune after inspecting real page output.
CODE_PATTERN = re.compile(r"(?<![A-Za-z0-9])(?=[A-Za-z0-9]{5,32}(?![A-Za-z0-9]))(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+(?![A-Za-z0-9])")


def fetch_codes():
    response = requests.get(URL, headers=HEADERS, timeout=25)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts/styles to avoid treating code snippets in JS as giftcodes.
    for node in soup(["script", "style", "noscript", "svg"]):
        node.decompose()

    found = {}
    for element in soup.select("code, [data-code], input[value], button, a"):
        raw = element.get("data-code") or element.get("value") or element.get_text(" ", strip=True)
        raw = raw.strip()
        if CODE_PATTERN.fullmatch(raw):
            found.setdefault(raw.upper(), {
                "code": raw,
                "reward": None,
                "status": "unknown",
                "source_url": URL,
            })

    # Also scan visible text tokens in case codes aren't inside dedicated elements.
    for token in CODE_PATTERN.findall(soup.get_text(" ", strip=True)):
        found.setdefault(token.upper(), {
            "code": token,
            "reward": None,
            "status": "unknown",
            "source_url": URL,
        })

    return list(found.values())
