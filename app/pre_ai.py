import re
from pathlib import Path


# ------------------------------------------------------------
# EMAIL
# ------------------------------------------------------------

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


def extract_emails(text):

    matches = EMAIL_PATTERN.findall(text)

    emails = []

    for email in matches:

        email = email.strip().lower()

        if email not in emails:
            emails.append(email)

    return emails


# ------------------------------------------------------------
# PHONE NUMBERS
# ------------------------------------------------------------

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+92|0092|92|0)"
    r"(?:[-.\s()]*)"
    r"(?:3\d{2})"
    r"(?:[-.\s]*\d{3})"
    r"(?:[-.\s]*\d{4})"
    r"(?!\d)"
)


def normalize_pakistan_phone(phone):

    digits = re.sub(r"\D", "", phone)

    if digits.startswith("0092"):
        digits = digits[4:]

    elif digits.startswith("92"):
        digits = digits[2:]

    elif digits.startswith("0"):
        digits = digits[1:]

    if len(digits) == 10 and digits.startswith("3"):
        return "+92" + digits

    return None


def extract_phones(text):

    matches = PHONE_PATTERN.findall(text)

    phones = []

    for match in matches:

        normalized = normalize_pakistan_phone(match)

        if normalized and normalized not in phones:
            phones.append(normalized)

    return phones


# ------------------------------------------------------------
# URLS
# ------------------------------------------------------------

URL_PATTERN = re.compile(
    r"\b(?:https?://|www\.)[^\s<>\"]+",
    re.IGNORECASE
)


def extract_urls(text):

    matches = URL_PATTERN.findall(text)

    urls = []

    for url in matches:

        url = url.rstrip(".,;:)]}")

        if url not in urls:
            urls.append(url)

    return urls


# ------------------------------------------------------------
# LINKEDIN
# ------------------------------------------------------------

def extract_linkedin(urls):

    linkedin_urls = []

    for url in urls:

        if "linkedin.com/" in url.lower():

            if url not in linkedin_urls:
                linkedin_urls.append(url)

    return linkedin_urls


# ------------------------------------------------------------
# KEYWORD SIGNALS
# ------------------------------------------------------------

KEYWORD_GROUPS = {

    "networking": [
        "cisco",
        "huawei",
        "h3c",
        "juniper",
        "arista",
        "routing",
        "switching",
        "bgp",
        "ospf",
        "mpls",
        "sd-wan",
        "network engineer",
        "network administrator",
        "network architect",
        "noc"
    ],

    "systems": [
        "dell",
        "dell emc",
        "hpe",
        "hp",
        "ibm",
        "lenovo",
        "netapp",
        "vmware",
        "nutanix",
        "proxmox",
        "hyper-v",
        "virtualization",
        "server",
        "storage",
        "systems engineer",
        "system administrator",
        "systems administrator"
    ],

    "cybersecurity": [
        "fortinet",
        "palo alto",
        "firewall",
        "siem",
        "soc",
        "xdr",
        "edr",
        "vapt",
        "penetration testing",
        "penetration tester",
        "cybersecurity",
        "cyber security",
        "information security",
        "security engineer",
        "security analyst"
    ],

    "software": [
        "python",
        "java",
        "javascript",
        "typescript",
        "react",
        "angular",
        "node.js",
        "nodejs",
        "flutter",
        "dart",
        "php",
        "c++",
        "c#",
        ".net",
        "software engineer",
        "software developer",
        "full stack",
        "full-stack",
        "frontend",
        "backend"
    ],

    "cloud": [
        "aws",
        "azure",
        "google cloud",
        "gcp",
        "cloud engineer",
        "cloud architect",
        "cloud computing",
        "private cloud",
        "hybrid cloud"
    ],

    "data_center": [
        "data center",
        "datacenter",
        "ups",
        "precision cooling",
        "hvac",
        "dcim",
        "rack",
        "structured cabling",
        "data center engineer",
        "data center facilities"
    ],

    "ai_ml": [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "generative ai",
        "computer vision",
        "natural language processing",
        "nlp",
        "pytorch",
        "tensorflow",
        "llm",
        "ai engineer",
        "machine learning engineer"
    ]
}


def extract_keyword_signals(text):

    text_lower = text.lower()

    results = {}

    for group, keywords in KEYWORD_GROUPS.items():

        found = []

        for keyword in keywords:

            if keyword.lower() in text_lower:

                if keyword not in found:
                    found.append(keyword)

        results[group] = found

    return results


# ------------------------------------------------------------
# CERTIFICATION SIGNALS
# ------------------------------------------------------------

CERTIFICATION_KEYWORDS = [

    "ccna",
    "ccnp",
    "ccie",
    "hcna",
    "hcna-datacom",
    "hcia",
    "hcip",
    "hcie",

    "comptia",
    "security+",
    "network+",

    "vmware certified",
    "vcp",
    "mcsa",
    "mcse",
    "microsoft certified",

    "aws certified",
    "azure certified",

    "ceh",
    "cissp",
    "cism",
    "crisc",
    "oscp",

    "itil",
    "pmp",
    "prince2"
]


def extract_certification_signals(text):

    text_lower = text.lower()

    found = []

    for certification in CERTIFICATION_KEYWORDS:

        if certification.lower() in text_lower:

            if certification not in found:
                found.append(certification)

    return found


# ------------------------------------------------------------
# DEGREE SIGNALS
# ------------------------------------------------------------

DEGREE_KEYWORDS = [

    "phd",
    "doctorate",

    "ms",
    "m.sc",
    "msc",
    "master",
    "mba",
    "mcs",
    "mit",
    "meng",

    "bs",
    "b.sc",
    "bsc",
    "bba",
    "be",
    "b.e",
    "bcs",
    "btech",
    "b.tech",

    "bachelor",

    "diploma"
]


def extract_degree_signals(text):

    text_lower = text.lower()

    found = []

    for degree in DEGREE_KEYWORDS:

        pattern = r"(?<![a-z])" + re.escape(degree.lower()) + r"(?![a-z])"

        if re.search(pattern, text_lower):

            if degree not in found:
                found.append(degree)

    return found


# ------------------------------------------------------------
# CV VALIDITY
# ------------------------------------------------------------

def assess_document(text):

    stripped = text.strip()

    character_count = len(stripped)

    word_count = len(stripped.split())

    if character_count < 100:

        status = "REVIEW"

    elif word_count < 30:

        status = "REVIEW"

    else:

        status = "VALID"

    return {
        "status": status,
        "character_count": character_count,
        "word_count": word_count
    }


# ------------------------------------------------------------
# MAIN PRE-AI PROCESSOR
# ------------------------------------------------------------

def run_pre_ai(text):

    urls = extract_urls(text)

    result = {

        "document_assessment": assess_document(text),

        "contact": {
            "emails": extract_emails(text),
            "phones": extract_phones(text),
            "linkedin": extract_linkedin(urls),
            "urls": urls
        },

        "signals": {
            "keywords": extract_keyword_signals(text),
            "certifications": extract_certification_signals(text),
            "degrees": extract_degree_signals(text)
        }
    }

    return result