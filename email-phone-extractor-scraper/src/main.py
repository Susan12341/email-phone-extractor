import argparse
import csv
import json
import os
import sys
import time
from typing import Dict, List, Set
from urllib.parse import urlparse

# Ensure module imports work when running as a script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from utils.logger import get_logger  # noqa: E402
from crawler.url_parser import normalize_url, is_same_domain  # noqa: E402
from crawler.html_analyzer import fetch_html, extract_links  # noqa: E402
from crawler.link_handler import LinkQueue  # noqa: E402
from extractors.contact_extractor import ContactExtractor  # noqa: E402
from exporters.json_exporter import JSONExporter  # noqa: E402
from exporters.csv_exporter import CSVExporter  # noqa: E402
from exporters.api_connector import APIConnector  # noqa: E402

def load_settings(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_input_urls(csv_path: str) -> List[str]:
    urls = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "url" not in [c.lower() for c in reader.fieldnames or []]:
            raise ValueError("input_urls.csv must contain a 'url' column header")
        # Preserve original case for header matching
        headers = reader.fieldnames or []
        url_key = next(h for h in headers if h.lower() == "url")
        for row in reader:
            val = (row.get(url_key) or "").strip()
            if val:
                urls.append(val)
    return urls

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def crawl_site(
    start_url: str,
    settings: Dict,
    logger,
    extractor: ContactExtractor,
) -> List[Dict]:
    """
    Crawl a single site starting from start_url, respecting domain boundaries
    and max_pages_per_site configuration.
    """
    parsed = urlparse(start_url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    max_pages = int(settings.get("crawl", {}).get("max_pages_per_site", 10))
    follow_links = bool(settings.get("crawl", {}).get("follow_links", True))

    results: List[Dict] = []
    visited: Set[str] = set()
    q = LinkQueue()
    q.push(normalize_url(start_url))

    while not q.empty() and len(visited) < max_pages:
        url = q.pop()
        if url in visited:
            continue
        visited.add(url)

        try:
            html, final_url, status = fetch_html(
                url,
                timeout=float(settings.get("network", {}).get("timeout_sec", 15)),
                retries=int(settings.get("network", {}).get("retries", 2)),
                backoff=float(settings.get("network", {}).get("backoff_sec", 1.0)),
                headers=settings.get("network", {}).get("headers", {}),
                logger=logger,
            )
        except Exception as e:
            logger.warning(f"Fetch failed for {url}: {e}")
            continue

        logger.info(f"Crawled {final_url} [{status}]")

        # Extract contact info from the page
        try:
            page_contacts = extractor.extract_all(final_url, html)
            if page_contacts:
                results.extend(page_contacts)
        except Exception as e:
            logger.error(f"Extraction error at {final_url}: {e}")

        # Queue internal links
        if follow_links:
            try:
                for link in extract_links(html, base=final_url):
                    nlink = normalize_url(link)
                    if (
                        nlink
                        and is_same_domain(base_domain, nlink)
                        and nlink not in visited
                    ):
                        q.push(nlink)
            except Exception as e:
                logger.debug(f"Link extraction error at {final_url}: {e}")

    return results

def dedupe_records(records: List[Dict]) -> List[Dict]:
    """
    Deduplicate by (email, phone, url) tuple where present.
    """
    seen = set()
    unique = []
    for r in records:
        key = (
            (r.get("email") or "").lower(),
            (r.get("phone") or "").replace(" ", ""),
            r.get("url") or "",
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique

def main():
    parser = argparse.ArgumentParser(
        description="Email & Phone Extractor — crawl websites and collect contacts."
    )
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(CURRENT_DIR), "config", "settings.json"),
        help="Path to settings.json",
    )
    parser.add_argument(
        "--input",
        default=os.path.join(os.path.dirname(CURRENT_DIR), "data", "input_urls.csv"),
        help="Path to CSV with a 'URL' column",
    )
    parser.add_argument(
        "--outdir",
        default=os.path.join(os.path.dirname(CURRENT_DIR), "data"),
        help="Directory to write outputs",
    )
    args = parser.parse_args()

    ensure_dir(args.outdir)
    logger = get_logger("extractor")

    # Load config and inputs
    settings = load_settings(args.config)
    try:
        urls = load_input_urls(args.input)
    except Exception as e:
        logger.error(f"Failed to read input URLs: {e}")
        sys.exit(1)

    if not urls:
        logger.error("No URLs provided in input file.")
        sys.exit(1)

    extractor = ContactExtractor(logger=logger)
    all_results: List[Dict] = []

    start_time = time.time()
    for url in urls:
        logger.info(f"Starting crawl: {url}")
        site_results = crawl_site(url, settings, logger, extractor)
        all_results.extend(site_results)

    # Deduplicate & sort
    all_results = dedupe_records(all_results)
    all_results.sort(key=lambda r: (r.get("email") or "", r.get("url") or ""))

    # Export
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    exporters = []
    formats = settings.get("output", {}).get("formats", ["json", "csv"])
    base_name = f"contacts_{timestamp}"

    if "json" in formats:
        exporters.append(
            JSONExporter(
                output_path=os.path.join(args.outdir, f"{base_name}.json"),
                indent=2,
            )
        )
    if "csv" in formats:
        exporters.append(
            CSVExporter(
                output_path=os.path.join(args.outdir, f"{base_name}.csv"),
                field_order=[
                    "email",
                    "phone",
                    "linkedin",
                    "twitter",
                    "instagram",
                    "facebook",
                    "youtube",
                    "logo",
                    "url",
                ],
            )
        )

    for exp in exporters:
        try:
            exp.export(all_results)
            logger.info(f"Exported: {exp.output_path}")
        except Exception as e:
            logger.error(f"Export failed for {exp.__class__.__name__}: {e}")

    # Optional API push
    api_conf = settings.get("api", {})
    if api_conf.get("enabled"):
        api = APIConnector(
            endpoint=api_conf.get("endpoint"),
            api_key=api_conf.get("api_key"),
            timeout=float(api_conf.get("timeout_sec", 20)),
            logger=logger,
        )
        try:
            sent = api.send_batch(all_results, batch_size=int(api_conf.get("batch_size", 500)))
            logger.info(f"API push complete. Batches sent: {sent}")
        except Exception as e:
            logger.error(f"API push failed: {e}")

    elapsed = time.time() - start_time
    logger.info(f"Done. {len(all_results)} records. Elapsed: {elapsed:.2f}s")

if __name__ == "__main__":
    main()