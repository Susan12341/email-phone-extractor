import re

# Email regex (simplified but robust for common cases)
EMAIL_RE = re.compile(
r"""
(?P<email>
[a-z0-9.!#$%&'*+/=?^_`{|}~-]+
@
[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?
(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+
)
""",
re.IGNORECASE | re.VERBOSE,
)

# Phone regex capturing international and local formats commonly found on pages
PHONE_RE = re.compile(
r"""
(?P<phone>
(?:(?:\+|00)\s?\d{1,3}[\s\-\.]?)?     # country code
(?:\(?\d{2,4}\)?[\s\-\.]?)?           # area/region code
\d{3,4}[\s\-\.]?\d{3,4}               # local number
(?:[\s\-\.]?\d{2,4})?                 # extension-like tail
)
""",
re.VERBOSE,
)

# Social profile patterns (domain anchored)
SOCIAL_PATTERNS = {
"linkedin": re.compile(r"https?://(www\.)?linkedin\.com/[A-Za-z0-9_\-\/?=%.]+", re.IGNORECASE),
"twitter": re.compile(r"https?://(www\.)?(twitter\.com|x\.com)/[A-Za-z0-9_\-\/?=%.]+", re.IGNORECASE),
"instagram": re.compile(r"https?://(www\.)?instagram\.com/[A-Za-z0-9_\-\/?=%.]+", re.IGNORECASE),
"facebook": re.compile(r"https?://(www\.)?facebook\.com/[A-Za-z0-9_\-\/?=%.]+", re.IGNORECASE),
"youtube": re.compile(r"https?://(www\.)?youtube\.com/[A-Za-z0-9_\-\/?=%.]+", re.IGNORECASE),
}

# Logo-like images (simple heuristic: logo in filename)
LOGO_RE = re.compile(
r"""https?://[^"'\s>]+?(?:logo|brand)[^"'\s>]*?\.(?:png|jpe?g|svg|webp)""",
re.IGNORECASE,
)