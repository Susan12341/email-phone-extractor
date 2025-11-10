from urllib.parse import urljoin, urlparse, urlunparse

def normalize_url(url: str, base: str | None = None) -> str:
    if not url:
        return ""
    url = url.strip()
    if base:
        url = urljoin(base, url)

    parsed = urlparse(url)
    if not parsed.scheme:
        # Assume http if scheme is missing, but keep netloc/path if present
        parsed = parsed._replace(scheme="http")
    # Remove fragments, normalize path
    parsed = parsed._replace(fragment="")
    # Optional: strip default ports
    netloc = parsed.netloc.replace(":80", "").replace(":443", "")
    parsed = parsed._replace(netloc=netloc)
    # Ensure trailing slash consistency for empty path
    if parsed.path == "":
        parsed = parsed._replace(path="/")
    return urlunparse(parsed)

def is_same_domain(base_domain: str, url: str) -> bool:
    """
    base_domain is expected like 'https://example.com'
    """
    if not base_domain or not url:
        return False
    b = urlparse(base_domain)
    u = urlparse(url)
    return b.netloc.lower() == u.netloc.lower()