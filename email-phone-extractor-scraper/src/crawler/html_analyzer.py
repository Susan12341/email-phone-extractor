from typing import List, Tuple
import time
import requests
from bs4 import BeautifulSoup
from .url_parser import normalize_url

def fetch_html(
    url: str,
    timeout: float = 15,
    retries: int = 2,
    backoff: float = 1.0,
    headers: dict | None = None,
    logger=None,
) -> Tuple[str, str, int]:
    """
    Fetch HTML with retries. Returns (html_text, final_url, status_code).
    """
    headers = headers or {
        "User-Agent": "Mozilla/5.0 (compatible; EmailPhoneExtractor/1.0; +https://example.com/bot)"
    }
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            resp.raise_for_status()
            return resp.text, resp.url, resp.status_code
        except Exception as e:
            last_exc = e
            if logger:
                logger.debug(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt))
    # Final try without raising to return status if any
    try:
        resp = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        status = resp.status_code
        return resp.text, resp.url, status
    except Exception:
        raise last_exc or RuntimeError("Unknown fetch error")

def extract_links(html: str, base: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("javascript:") or href.startswith("#"):
            continue
        links.append(normalize_url(href, base=base))
    return links