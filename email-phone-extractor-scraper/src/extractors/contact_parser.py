thonimport requests
from bs4 import BeautifulSoup
import re

def parse_contact_info(url):
    """
    Extract contact information (emails, phone numbers, social media) from a given webpage.
    
    :param url: The URL to scrape.
    :return: A dictionary containing the extracted contact information.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    contact_info = {
        "email": extract_email(soup),
        "phone": extract_phone(soup),
        "linkedin": extract_social_media(soup, "linkedin"),
        "twitter": extract_social_media(soup, "twitter"),
        "instagram": extract_social_media(soup, "instagram"),
        "facebook": extract_social_media(soup, "facebook"),
        "youtube": extract_social_media(soup, "youtube"),
    }
    
    return contact_info

def extract_email(soup):
    """Extract email addresses from the soup."""
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_regex, str(soup))
    return emails[0] if emails else None

def extract_phone(soup):
    """Extract phone numbers from the soup."""
    phone_regex = r"\+?[0-9]*[\s\-]?[0-9]+[\s\-]?[0-9]+[\s\-]?[0-9]+"
    phones = re.findall(phone_regex, str(soup))
    return phones[0] if phones else None

def extract_social_media(soup, platform):
    """Extract social media links based on the platform."""
    platform_urls = {
        "linkedin": r"https://www.linkedin.com/in/[a-zA-Z0-9_-]+",
        "twitter": r"https://x.com/[a-zA-Z0-9_-]+",
        "instagram": r"https://www.instagram.com/[a-zA-Z0-9_-]+",
        "facebook": r"https://www.facebook.com/[a-zA-Z0-9._-]+",
        "youtube": r"https://www.youtube.com/[a-zA-Z0-9_-]+",
    }
    
    regex = platform_urls.get(platform)
    if regex:
        links = re.findall(regex, str(soup))
        return links[0] if links else None
    return None