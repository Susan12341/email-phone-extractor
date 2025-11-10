from typing import Dict, List
from bs4 import BeautifulSoup
from .regex_patterns import EMAIL_RE, PHONE_RE, LOGO_RE
from .social_finder import find_socials

class ContactExtractor:
    """
    Extracts emails, phone numbers, social profiles, and a likely logo URL from an HTML page.
    """

    def __init__(self, logger=None):
        self.logger = logger

    def _extract_emails(self, text: str) -> List[str]:
        emails = set()
        for m in EMAIL_RE.finditer(text):
            email = m.group("email").strip().strip(".,;)")
            # Heuristic: skip common placeholders
            if "example.com" in email.lower() or "@" not in email:
                continue
            emails.add(email)
        return sorted(emails)

    def _extract_phones(self, text: str) -> List[str]:
        phones = set()
        for m in PHONE_RE.finditer(text):
            phone = " ".join(m.group("phone").split())
            # Filter too short numbers
            digits = [c for c in phone if c.isdigit()]
            if len(digits) < 7:
                continue
            phones.add(phone)
        return sorted(phones)

    def _extract_logo(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "lxml")
        # 1) Look for common logo selectors
        for sel in ["img[alt*=logo i]", "img[alt*=Logo i]", "img[src*='logo']"]:
            el = soup.select_one(sel)
            if el and el.get("src"):
                return el["src"]
        # 2) Regex fallback
        m = LOGO_RE.search(html)
        if m:
            return m.group(0)
        return None

    def extract_all(self, page_url: str, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text("\n", strip=True)

        emails = self._extract_emails(text)
        phones = self._extract_phones(text)
        socials = find_socials(html)
        logo = self._extract_logo(html)

        # Build cartesian combos but keep it compact:
        results: List[Dict] = []
        if not emails and not phones and not socials:
            # If nothing extracted, still return a stub row with url only (optional)
            return []

        # Prefer pairing first email/phone, but also emit extra rows for remaining values
        max_len = max(len(emails) or 1, len(phones) or 1)
        for i in range(max_len):
            rec = {
                "email": emails[i] if i < len(emails) else (emails[0] if emails else None),
                "phone": phones[i] if i < len(phones) else (phones[0] if phones else None),
                "linkedin": socials.get("linkedin"),
                "twitter": socials.get("twitter"),
                "instagram": socials.get("instagram"),
                "facebook": socials.get("facebook"),
                "youtube": socials.get("youtube"),
                "logo": logo,
                "url": page_url,
            }
            results.append(rec)

        return results