from bs4 import BeautifulSoup
from .regex_patterns import SOCIAL_PATTERNS

def find_socials(html: str) -> dict:
    """
    Extract social profile links from raw HTML using both anchor tags and regex fallback.
    """
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    candidates = {k: set() for k in SOCIAL_PATTERNS.keys()}

    # Anchor tag harvesting
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        for key, rx in SOCIAL_PATTERNS.items():
            if rx.search(href):
                candidates[key].add(href)

    # Regex fallback on text blob
    for key, rx in SOCIAL_PATTERNS.items():
        for m in rx.finditer(text):
            candidates[key].add(m.group(0))

    # Pick a deterministic single link per platform (the shortest)
    result = {}
    for k, vals in candidates.items():
        if vals:
            result[k] = sorted(vals, key=len)[0]
    return result