import json
import re

if __package__:
    from .app_paths import config_file
else:
    from app_paths import config_file

# ============================================================
# TECHNOLOGY KNOWLEDGE BASE
# ============================================================

TECHNOLOGY_PATTERNS = {

    # -----------------------------
    # Routing
    # -----------------------------

    "BGP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Routing",
    },

    "OSPF": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Routing",
    },

    "EIGRP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Routing",
    },

    "RIP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Routing",
    },

    "MPLS": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "WAN / Carrier",
    },

    "SD-WAN": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "WAN / SD-WAN",
    },

    "SDN": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Architecture / Automation",
    },

    # -----------------------------
    # Switching
    # -----------------------------

    "VLAN": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Switching",
    },

    "STP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Switching",
    },

    "RSTP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Switching",
    },

    "MSTP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Switching",
    },

    "EtherChannel": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Switching",
    },

    "HSRP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "High Availability",
    },

    "VRRP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "High Availability",
    },

    "GLBP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "High Availability",
    },

    # -----------------------------
    # IP / Network Services
    # -----------------------------

    "IPv4": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "IP",
    },

    "IPv6": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "IP",
    },

    "TCP/IP": {
        "type": "protocol_suite",
        "domain": "IP Datacom / Networking",
        "subcategory": "Networking",
    },

    "DHCP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Services",
    },

    "DNS": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Services",
    },

    "ARP": {
        "type": "protocol",
        "domain": "IP Datacom / Networking",
        "subcategory": "IP",
    },

    # -----------------------------
    # Network Security
    # -----------------------------

    "ACL": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Security",
    },

    "Port Security": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Security",
    },

    "DHCP Snooping": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Security",
    },

    "AAA": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Security",
    },

    "Firewall": {
        "type": "technology",
        "domain": "Cybersecurity",
        "subcategory": "Network Security",
    },

    # -----------------------------
    # Data Center Networking
    # -----------------------------

    "VXLAN": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Data Center Networking",
    },

    "EVPN": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Data Center Networking",
    },

    "Cisco ACI": {
        "type": "platform",
        "domain": "IP Datacom / Networking",
        "subcategory": "Data Center Networking",
    },

    # -----------------------------
    # Wireless
    # -----------------------------

    "Wi-Fi": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Wireless",
    },

    "WLAN": {
        "type": "technology",
        "domain": "IP Datacom / Networking",
        "subcategory": "Wireless",
    },

    # -----------------------------
    # Systems / Virtualization
    # -----------------------------

    "VMware": {
        "type": "platform",
        "domain": "IT Systems",
        "subcategory": "Virtualization",
    },

    "Hyper-V": {
        "type": "platform",
        "domain": "IT Systems",
        "subcategory": "Virtualization",
    },

    "Linux": {
        "type": "operating_system",
        "domain": "IT Systems",
        "subcategory": "Linux Systems",
    },

    "RHEL": {
        "type": "operating_system",
        "domain": "IT Systems",
        "subcategory": "Linux Systems",
    },

    "CentOS": {
        "type": "operating_system",
        "domain": "IT Systems",
        "subcategory": "Linux Systems",
    },

    "Ubuntu": {
        "type": "operating_system",
        "domain": "IT Systems",
        "subcategory": "Linux Systems",
    },

    "Windows Server": {
        "type": "operating_system",
        "domain": "IT Systems",
        "subcategory": "Windows Systems",
    },

    # -----------------------------
    # Monitoring / Operations
    # -----------------------------

    "SolarWinds": {
        "type": "tool",
        "domain": "IT Operations",
        "subcategory": "Monitoring",
    },

    "SolarWinds NPM": {
        "type": "tool",
        "domain": "IT Operations",
        "subcategory": "Network Monitoring",
    },

    "ManageEngine": {
        "type": "tool",
        "domain": "IT Operations",
        "subcategory": "Monitoring",
    },

    "SNMP": {
        "type": "protocol",
        "domain": "IT Operations",
        "subcategory": "Monitoring",
    },

    "Syslog": {
        "type": "technology",
        "domain": "IT Operations",
        "subcategory": "Logging / Monitoring",
    },

    # -----------------------------
    # Network Administration Tools
    # -----------------------------

    "EVE-NG": {
        "type": "tool",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Simulation",
    },

    "PuTTY": {
        "type": "tool",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Administration",
    },

    "SecureCRT": {
        "type": "tool",
        "domain": "IP Datacom / Networking",
        "subcategory": "Network Administration",
    },
}


# ============================================================
# OEM / VENDOR KNOWLEDGE
# ============================================================

OEM_PATTERNS = {

    "Cisco": {
        "domain": "IP Datacom / Networking",
    },

    "Huawei": {
        "domain": "IP Datacom / Networking",
    },

    "H3C": {
        "domain": "IP Datacom / Networking",
    },

    "Juniper Networks": {
        "domain": "IP Datacom / Networking",
    },

    "Aruba": {
        "domain": "IP Datacom / Networking",
    },

    "Dell Technologies": {
        "domain": "IT Systems",
    },

    "HPE": {
        "domain": "IT Systems",
    },

    "Lenovo": {
        "domain": "IT Systems",
    },

    "IBM": {
        "domain": "IT Systems",
    },

    "NetApp": {
        "domain": "IT Systems",
    },

    "Pure Storage": {
        "domain": "IT Systems",
    },

    "Nutanix": {
        "domain": "IT Systems",
    },

    "Sangfor": {
        "domain": "IT Systems",
    },

    "Proxmox": {
        "domain": "IT Systems",
    },

    "VMware": {
        "domain": "IT Systems",
    },

    "xFusion": {
        "domain": "IT Systems",
    },

    "Commvault": {
        "domain": "IT Systems",
    },

    "Veeam": {
        "domain": "IT Systems",
    },

    "Rubrik": {
        "domain": "IT Systems",
    },

    "Cohesity": {
        "domain": "IT Systems",
    },

    # Security
    "Fortinet": {
        "domain": "Cybersecurity",
    },

    "Palo Alto Networks": {
        "domain": "Cybersecurity",
    },

    "Check Point": {
        "domain": "Cybersecurity",
    },

    "Barracuda": {
        "domain": "Cybersecurity",
    },

    "CrowdStrike": {
        "domain": "Cybersecurity",
    },

    "Sophos": {
        "domain": "Cybersecurity",
    },

    "Trend Micro": {
        "domain": "Cybersecurity",
    },

    "Kaspersky": {
        "domain": "Cybersecurity",
    },

    "CyberArk": {
        "domain": "Cybersecurity",
    },

    "Delinea": {
        "domain": "Cybersecurity",
    },

    "BeyondTrust": {
        "domain": "Cybersecurity",
    },

    "Proofpoint": {
        "domain": "Cybersecurity",
    },

    "Splunk": {
        "domain": "Cybersecurity",
    },

    "LogRhythm": {
        "domain": "Cybersecurity",
    },

    "Logpoint": {
        "domain": "Cybersecurity",
    },

    # Cloud
    "Microsoft Azure": {
        "domain": "Cloud",
    },

    "AWS": {
        "domain": "Cloud",
    },

    "Google Cloud": {
        "domain": "Cloud",
    },

    "Oracle Cloud": {
        "domain": "Cloud",
    },
}


CATALOG_PATH = config_file("technology_catalog.json")


def _load_technology_catalog():
    try:
        with CATALOG_PATH.open("r", encoding="utf-8") as file:
            catalog = json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Technology catalog is missing: {CATALOG_PATH}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid technology catalog JSON at {CATALOG_PATH}: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(catalog.get("skills"), list) or not isinstance(
        catalog.get("vendors"), list
    ):
        raise ValueError(
            "Technology catalog must contain 'skills' and 'vendors' lists"
        )
    return catalog


TECHNOLOGY_CATALOG = _load_technology_catalog()
TECHNOLOGY_ALIASES = {}

for skill_group in TECHNOLOGY_CATALOG["skills"]:
    tier_1_terms = set(skill_group.get("tier_1_terms", []))
    tier_2_terms = set(skill_group.get("tier_2_terms", []))
    legacy_terms = set(skill_group.get("legacy_terms", []))
    for name, aliases in skill_group.get("terms", {}).items():
        existing = TECHNOLOGY_PATTERNS.get(name)
        if existing is None:
            existing = {
                "type": "technology",
                "domain": skill_group["domain"],
                "subcategory": skill_group["subcategory"],
            }
            TECHNOLOGY_PATTERNS[name] = existing
        configured_tier = skill_group.get("signal_tier", "")
        existing["signal_tier"] = (
            "tier_1"
            if name in tier_1_terms
            else "tier_2"
            if name in tier_2_terms
            else configured_tier
            if configured_tier in {"tier_1", "tier_2", "tier_3"}
            else "tier_3"
            if skill_group["subcategory"] == "Programming and web development"
            else "tier_2"
        )
        existing["legacy"] = name in legacy_terms or any(
            alias in legacy_terms for alias in aliases
        )
        TECHNOLOGY_ALIASES[name] = list(
            dict.fromkeys([*TECHNOLOGY_ALIASES.get(name, []), *aliases])
        )

for skill_group in TECHNOLOGY_CATALOG["skills"]:
    for name in skill_group.get("tier_1_terms", []):
        if name in TECHNOLOGY_PATTERNS:
            TECHNOLOGY_PATTERNS[name]["signal_tier"] = "tier_1"
    for name in skill_group.get("tier_2_terms", []):
        if name in TECHNOLOGY_PATTERNS:
            TECHNOLOGY_PATTERNS[name]["signal_tier"] = "tier_2"
    for name in skill_group.get("legacy_terms", []):
        if name in TECHNOLOGY_PATTERNS:
            TECHNOLOGY_PATTERNS[name]["legacy"] = True
        for canonical, aliases in TECHNOLOGY_ALIASES.items():
            if name in aliases:
                TECHNOLOGY_PATTERNS[canonical]["legacy"] = True
    for category, names in skill_group.get(
        "software_categories",
        {},
    ).items():
        for name in names:
            if name in TECHNOLOGY_PATTERNS:
                TECHNOLOGY_PATTERNS[name]["category"] = category

OEM_CATALOG = {}

for name, metadata in OEM_PATTERNS.items():
    OEM_CATALOG[name] = {
        "aliases": [],
        "parent_company": "",
        "domains": [metadata["domain"]],
        "products": [],
        "product_domains": {},
    }

for vendor in TECHNOLOGY_CATALOG["vendors"]:
    name = vendor["name"]
    entry = OEM_CATALOG.setdefault(
        name,
        {
            "aliases": [],
            "parent_company": "",
            "domains": [],
            "products": [],
            "product_domains": {},
        },
    )
    entry["aliases"] = list(
        dict.fromkeys([*entry["aliases"], *vendor.get("aliases", [])])
    )
    entry["products"] = list(
        dict.fromkeys([*entry["products"], *vendor.get("products", [])])
    )
    entry["domains"] = list(
        dict.fromkeys([*entry["domains"], *vendor.get("domains", [])])
    )
    entry["parent_company"] = (
        vendor.get("parent_company") or entry["parent_company"]
    )
    entry["product_domains"].update(vendor.get("product_domains", {}))


def _compile_exact_terms(terms):
    alternatives = "|".join(
        re.escape(term)
        for term in sorted(set(terms), key=len, reverse=True)
    )
    return re.compile(r"(?<!\w)(?:" + alternatives + r")(?!\w)", re.I)


TECHNOLOGY_MATCHERS = []
for technology, metadata in TECHNOLOGY_PATTERNS.items():
    variants = [technology, *TECHNOLOGY_ALIASES.get(technology, [])]
    matcher = _compile_exact_terms(variants)
    TECHNOLOGY_MATCHERS.append((technology, metadata, matcher))
TECHNOLOGY_MATCHERS.sort(
    key=lambda item: len(item[2].pattern),
    reverse=True,
)

OEM_MATCHERS = []
for oem, metadata in OEM_CATALOG.items():
    variants = [oem, *metadata["aliases"], *metadata["products"]]
    matcher = _compile_exact_terms(variants)
    OEM_MATCHERS.append((oem, metadata, matcher))
OEM_MATCHERS.sort(
    key=lambda item: len(item[2].pattern),
    reverse=True,
)


# ============================================================
# ROLE / CAREER FUNCTION KNOWLEDGE
# ============================================================

ROLE_PATTERNS = {

    # Networking
    "Network Engineer": {
        "domain": "IP Datacom / Networking",
        "career_function": "Engineering",
    },

    "Network Administrator": {
        "domain": "IP Datacom / Networking",
        "career_function": "Operations",
    },

    "Network Architect": {
        "domain": "IP Datacom / Networking",
        "career_function": "Architecture",
    },

    "Network Consultant": {
        "domain": "IP Datacom / Networking",
        "career_function": "Consulting",
    },

    "Network Presales": {
        "domain": "IP Datacom / Networking",
        "career_function": "Presales",
    },

    "Network Sales": {
        "domain": "IP Datacom / Networking",
        "career_function": "Sales",
    },

    # Systems
    "System Administrator": {
        "domain": "IT Systems",
        "career_function": "Operations",
    },

    "Systems Engineer": {
        "domain": "IT Systems",
        "career_function": "Engineering",
    },

    "Systems Architect": {
        "domain": "IT Systems",
        "career_function": "Architecture",
    },

    # Security
    "Security Engineer": {
        "domain": "Cybersecurity",
        "career_function": "Engineering",
    },

    "Cybersecurity Engineer": {
        "domain": "Cybersecurity",
        "career_function": "Engineering",
    },

    "SOC Analyst": {
        "domain": "Cybersecurity",
        "career_function": "Operations",
    },

    "Security Architect": {
        "domain": "Cybersecurity",
        "career_function": "Architecture",
    },

    # Software
    "Software Engineer": {
        "domain": "Software",
        "career_function": "Engineering",
    },

    "Software Developer": {
        "domain": "Software",
        "career_function": "Engineering",
    },

    "Full Stack Developer": {
        "domain": "Software",
        "career_function": "Engineering",
    },

    "Frontend Developer": {
        "domain": "Software",
        "career_function": "Frontend / UI Development",
    },

    "Backend Developer": {
        "domain": "Software",
        "career_function": "Backend Development",
    },

    "DevOps Engineer": {
        "domain": "Cloud",
        "career_function": "DevOps / Platform Engineering",
    },

    "Site Reliability Engineer": {
        "domain": "Cloud",
        "career_function": "DevOps / Platform Engineering",
    },

    "Platform Engineer": {
        "domain": "IT Systems",
        "career_function": "DevOps / Platform Engineering",
    },

    "Data Engineer": {
        "domain": "Software",
        "career_function": "Data Engineering / BI",
    },

    "Machine Learning Engineer": {
        "domain": "AI / Machine Learning",
        "career_function": "AI / Machine Learning",
    },

    "ML Engineer": {
        "domain": "AI / Machine Learning",
        "career_function": "AI / Machine Learning",
    },

    "Data Scientist": {
        "domain": "AI / Machine Learning",
        "career_function": "AI / Machine Learning",
    },

    "QA Engineer": {
        "domain": "Software",
        "career_function": "Quality Assurance / Testing",
    },

    "Test Engineer": {
        "domain": "Software",
        "career_function": "Quality Assurance / Testing",
    },

    "UX Designer": {
        "domain": "Software",
        "career_function": "Product / UX Design",
    },

    # Business
    "HR Executive": {
        "domain": "Human Resources",
        "career_function": "HR",
    },

    "HR Manager": {
        "domain": "Human Resources",
        "career_function": "Management",
    },

    "Recruiter": {
        "domain": "Human Resources",
        "career_function": "Recruitment",
    },

    "Talent Acquisition": {
        "domain": "Human Resources",
        "career_function": "Recruitment",
    },

    "Finance Manager": {
        "domain": "Finance & Accounting",
        "career_function": "Finance",
    },

    "Accountant": {
        "domain": "Finance & Accounting",
        "career_function": "Accounting",
    },

    "Project Manager": {
        "domain": "Project Management",
        "career_function": "Management",
    },
}


# ============================================================
# ACTION VERBS
# ============================================================

ACTION_PATTERNS = [

    "configured",
    "configure",
    "configuring",

    "deployed",
    "deploy",
    "deploying",

    "implemented",
    "implement",
    "implementing",

    "installed",
    "install",
    "installing",

    "managed",
    "manage",
    "managing",

    "maintained",
    "maintain",
    "maintaining",

    "supported",
    "support",
    "supporting",

    "troubleshot",
    "troubleshoot",
    "troubleshooting",

    "designed",
    "design",
    "designing",

    "architected",
    "architect",
    "architecting",

    "administered",
    "administer",
    "administering",

    "monitored",
    "monitor",
    "monitoring",

    "optimized",
    "optimised",
    "optimize",
    "optimise",

    "provisioned",
    "provision",
    "provisioning",

    "migrated",
    "migrate",
    "migrating",

    "automated",
    "automate",
    "automating",

    "secured",
    "secure",
    "securing",

    "resolved",
    "resolve",
    "resolving",

    "analyzed",
    "analysed",
    "analyze",
    "analysing",
]


# ============================================================
# SECTION DETECTION
# ============================================================

SECTION_HEADERS = {
    "experience": [
        "experience",
        "professional experience",
        "work experience",
        "employment history",
        "career history",
        "professional background",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "core competencies",
        "competencies",
        "technical competencies",
        "expertise",
    ],

    "certifications": [
        "certifications",
        "certification",
        "professional certifications",
        "licenses and certifications",
    ],

    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "qualifications",
    ],
}


def detect_section(text, position):

    """
    Determine the most likely CV section surrounding a
    technology occurrence.

    This is deliberately conservative.
    """

    before = text[:position]

    current_section = "unknown"
    current_position = -1

    for section, headers in SECTION_HEADERS.items():

        for header in headers:

            pattern = (
                r"(?im)^\s*"
                + re.escape(header)
                + r"\s*:?\s*$"
            )

            for match in re.finditer(
                pattern,
                before
            ):

                if match.start() > current_position:

                    current_position = match.start()
                    current_section = section

    return current_section


# ============================================================
# TEXT / CONTEXT HELPERS
# ============================================================

def get_line_context(text, start, end):

    """
    Return the complete line containing the match.
    """

    line_start = text.rfind(
        "\n",
        0,
        start
    )

    line_end = text.find(
        "\n",
        end
    )

    if line_start == -1:
        line_start = 0
    else:
        line_start += 1

    if line_end == -1:
        line_end = len(text)

    return text[line_start:line_end].strip()


def get_nearby_context(text, start, end, window=120):

    context_start = max(
        0,
        start - window
    )

    context_end = min(
        len(text),
        end + window
    )

    return text[
        context_start:context_end
    ].strip()


def detect_actions(text):

    actions = []

    text_lower = text.lower()

    for action in ACTION_PATTERNS:

        pattern = (
            r"(?<!\w)"
            + re.escape(action)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text_lower
        ):

            if action not in actions:
                actions.append(action)

    return actions


# ============================================================
# ACTION -> TECHNOLOGY RELATIONSHIP
# ============================================================

def detect_explicit_action_relation(
    line,
    technology
):

    """
    Determine whether the technology and an action
    occur in the same sentence/line.

    This is still deterministic and intentionally
    conservative.
    """

    line_lower = line.lower()

    technology_pattern = (
        r"(?<!\w)"
        + re.escape(technology.lower())
        + r"(?!\w)"
    )

    technology_match = re.search(
        technology_pattern,
        line_lower
    )

    if not technology_match:
        return []

    actions = []

    for action in ACTION_PATTERNS:

        action_pattern = (
            r"(?<!\w)"
            + re.escape(action)
            + r"(?!\w)"
        )

        action_match = re.search(
            action_pattern,
            line_lower
        )

        if not action_match:
            continue

        distance = abs(
            technology_match.start()
            - action_match.start()
        )

        # Conservative relationship threshold.
        if distance <= 80:

            if action not in actions:
                actions.append(action)

    return actions


# ============================================================
# EVIDENCE STRENGTH
# ============================================================

def determine_evidence_type(
    section,
    explicit_actions,
    line
):

    """
    Classify the type of evidence.

    This is NOT a competence judgment.
    """

    if explicit_actions:

        return "PRACTICAL_ACTION"

    if section == "experience":

        return "EXPERIENCE_MENTION"

    if section == "skills":

        return "SKILL_MENTION"

    if section == "certifications":

        return "CERTIFICATION_CONTEXT"

    return "MENTION"


def determine_evidence_strength(
    evidence_type
):

    if evidence_type == "PRACTICAL_ACTION":
        return "strong"

    if evidence_type == "EXPERIENCE_MENTION":
        return "moderate"

    if evidence_type == "SKILL_MENTION":
        return "weak"

    if evidence_type == "CERTIFICATION_CONTEXT":
        return "context_only"

    return "weak"


# ============================================================
# TECHNOLOGY OCCURRENCES
# ============================================================

def extract_technology_occurrences(text):

    occurrences = []

    for technology, metadata, pattern in TECHNOLOGY_MATCHERS:
        for match in pattern.finditer(text):

            line = get_line_context(
                text,
                match.start(),
                match.end()
            )

            context = get_nearby_context(
                text,
                match.start(),
                match.end()
            )

            section = detect_section(
                text,
                match.start()
            )

            explicit_actions = (
                detect_explicit_action_relation(
                    line,
                    technology
                )
            )

            evidence_type = (
                determine_evidence_type(
                    section,
                    explicit_actions,
                    line
                )
            )

            evidence_strength = (
                determine_evidence_strength(
                    evidence_type
                )
            )

            occurrences.append({

                "name_raw": match.group(0),

                "normalized_name": technology,

                "type": metadata["type"],

                "category": metadata.get("category", ""),

                "domain": metadata["domain"],

                "subcategory": metadata["subcategory"],

                "signal_tier": metadata.get("signal_tier", ""),

                "legacy": metadata.get("legacy", False),

                "section": section,

                "evidence_type": evidence_type,

                "evidence_strength": evidence_strength,

                "explicit_actions": explicit_actions,

                "line_evidence": line,

                "context_evidence": context,

                "character_start": match.start(),

                "character_end": match.end(),

            })

    return occurrences


# ============================================================
# TECHNOLOGY SUMMARY
# ============================================================

def build_technology_summary(
    occurrences
):

    summary = {}

    for occurrence in occurrences:

        name = occurrence[
            "normalized_name"
        ]

        if name not in summary:

            summary[name] = {

                "normalized_name": name,

                "type": occurrence["type"],

                "category": occurrence.get("category", ""),

                "domain": occurrence["domain"],

                "subcategory": occurrence[
                    "subcategory"
                ],

                "signal_tier": occurrence.get("signal_tier", ""),

                "legacy": occurrence.get("legacy", False),

                "occurrence_count": 0,

                "practical_evidence_count": 0,

                "experience_mention_count": 0,

                "skill_mention_count": 0,

                "certification_context_count": 0,

                "mention_count": 0,

            }

        item = summary[name]

        item["occurrence_count"] += 1
        tier_priority = {"tier_1": 1, "tier_2": 2, "tier_3": 3}
        current_tier = item.get("signal_tier", "")
        occurrence_tier = occurrence.get("signal_tier", "")
        if (
            occurrence_tier
            and (
                not current_tier
                or tier_priority.get(occurrence_tier, 4)
                < tier_priority.get(current_tier, 4)
            )
        ):
            item["signal_tier"] = occurrence_tier
        item["legacy"] = item["legacy"] or occurrence.get("legacy", False)

        evidence_type = occurrence[
            "evidence_type"
        ]

        if evidence_type == "PRACTICAL_ACTION":

            item[
                "practical_evidence_count"
            ] += 1

        elif evidence_type == "EXPERIENCE_MENTION":

            item[
                "experience_mention_count"
            ] += 1

        elif evidence_type == "SKILL_MENTION":

            item[
                "skill_mention_count"
            ] += 1

        elif evidence_type == "CERTIFICATION_CONTEXT":

            item[
                "certification_context_count"
            ] += 1

        else:

            item[
                "mention_count"
            ] += 1

    return list(
        summary.values()
    )


# ============================================================
# OEM EXTRACTION
# ============================================================

def extract_oems(text):

    records = []

    for oem, metadata, pattern in OEM_MATCHERS:
        for match in pattern.finditer(text):

            line = get_line_context(
                text,
                match.start(),
                match.end()
            )

            section = detect_section(
                text,
                match.start()
            )
            matched_term = match.group(0)
            product_line = next(
                (
                    product
                    for product in metadata["products"]
                    if product.casefold() == matched_term.casefold()
                ),
                "",
            )

            matched_domains = (
                metadata["product_domains"].get(
                    product_line,
                    metadata["domains"][:1],
                )
                if product_line
                else metadata["domains"]
            )
            records.append({

                "name_raw": matched_term,

                "normalized_name": oem,

                "type": "OEM",

                "domain": (
                    matched_domains[0] if matched_domains else ""
                ),

                "domains": matched_domains,

                "parent_company": metadata["parent_company"],

                "product_line": product_line,

                "section": section,

                "evidence": line,

                "character_start": match.start(),

                "character_end": match.end(),

            })

    return records


# ============================================================
# ROLE EXTRACTION
# ============================================================

def extract_roles(text):

    records = []

    patterns = sorted(
        ROLE_PATTERNS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for role, metadata in patterns:

        pattern = (
            r"(?<!\w)"
            + re.escape(role)
            + r"(?!\w)"
        )

        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE
        ):

            line = get_line_context(
                text,
                match.start(),
                match.end()
            )

            section = detect_section(
                text,
                match.start()
            )

            records.append({

                "name_raw": match.group(0),

                "normalized_name": role,

                "domain": metadata["domain"],

                "career_function": metadata[
                    "career_function"
                ],

                "section": section,

                "evidence": line,

                "character_start": match.start(),

                "character_end": match.end(),

            })

    return records


# ============================================================
# DOMAIN SIGNALS
# ============================================================

def build_domain_signals(
    technology_occurrences,
    oems,
    roles
):

    domains = {}

    def ensure_domain(domain):

        if domain not in domains:

            domains[domain] = {

                "domain": domain,

                "technology_occurrences": 0,

                "oem_occurrences": 0,

                "product_occurrences": 0,

                "role_occurrences": 0,

                "practical_action_occurrences": 0,

            }

    for item in technology_occurrences:

        domain = item["domain"]

        ensure_domain(domain)

        domains[domain][
            "technology_occurrences"
        ] += 1

        if item["evidence_type"] == (
            "PRACTICAL_ACTION"
        ):

            domains[domain][
                "practical_action_occurrences"
            ] += 1

    for item in oems:
        mapped_domains = item.get("domains") or [item.get("domain", "")]
        for domain in mapped_domains:
            if not domain:
                continue
            ensure_domain(domain)
            domains[domain]["oem_occurrences"] += 1
            if item.get("product_line"):
                domains[domain]["product_occurrences"] += 1

    for item in roles:

        domain = item["domain"]

        ensure_domain(domain)

        domains[domain][
            "role_occurrences"
        ] += 1

    return list(
        domains.values()
    )


# ============================================================
# PUBLIC API
# ============================================================

def extract_technology_evidence(text):

    technology_occurrences = (
        extract_technology_occurrences(
            text
        )
    )

    technology_summary = (
        build_technology_summary(
            technology_occurrences
        )
    )

    oems = extract_oems(
        text
    )

    roles = extract_roles(
        text
    )

    domain_signals = build_domain_signals(
        technology_occurrences,
        oems,
        roles
    )

    return {

        # Individual evidence occurrences
        "technology_occurrences":
            technology_occurrences,

        # Deduplicated technology view
        "technology_summary":
            technology_summary,

        # OEM evidence
        "oems":
            oems,

        # Role evidence
        "roles":
            roles,

        # Domain signals only.
        # NOT final candidate classification.
        "domain_signals":
            domain_signals,

        "technology_count":
            len(technology_summary),

        "technology_occurrence_count":
            len(technology_occurrences),

        "oem_count":
            len(oems),

        "role_count":
            len(roles),

    }


# ============================================================
# DISPLAY
# ============================================================

def print_technology_summary(result):

    print("=" * 70)
    print(
        "TECHNOLOGY / TERMINOLOGY / EVIDENCE EXTRACTION V2"
    )
    print("=" * 70)

    print(
        f"Unique technologies: "
        f"{result.get('technology_count', 0)}"
    )

    print(
        f"Technology occurrences: "
        f"{result.get('technology_occurrence_count', 0)}"
    )

    print(
        f"OEM occurrences: "
        f"{result.get('oem_count', 0)}"
    )

    print(
        f"Role occurrences: "
        f"{result.get('role_count', 0)}"
    )

    print()
    print("TECHNOLOGY SUMMARY")
    print("-" * 70)

    for item in result.get(
        "technology_summary",
        []
    ):

        print(
            f"  - {item['normalized_name']} "
            f"[{item['type']}] "
            f"[{item['subcategory']}]"
        )

        print(
            f"    Occurrences: "
            f"{item['occurrence_count']} | "
            f"Practical: "
            f"{item['practical_evidence_count']} | "
            f"Experience: "
            f"{item['experience_mention_count']} | "
            f"Skills: "
            f"{item['skill_mention_count']} | "
            f"Other: "
            f"{item['mention_count']}"
        )

    print()
    print("OEMs")
    print("-" * 70)

    seen_oems = set()

    for item in result.get(
        "oems",
        []
    ):

        name = item[
            "normalized_name"
        ]

        if name in seen_oems:
            continue

        seen_oems.add(name)

        print(
            f"  - {name} "
            f"[{item['domain']}]"
        )

    print()
    print("ROLES")
    print("-" * 70)

    seen_roles = set()

    for item in result.get(
        "roles",
        []
    ):

        role = item[
            "normalized_name"
        ]

        if role in seen_roles:
            continue

        seen_roles.add(role)

        print(
            f"  - {role} "
            f"[{item['domain']}] "
            f"[{item['career_function']}]"
        )

    print()
    print("DOMAIN SIGNALS")
    print("-" * 70)

    for item in result.get(
        "domain_signals",
        []
    ):

        print(
            f"  - {item['domain']}: "
            f"technologies="
            f"{item['technology_occurrences']}, "
            f"OEMs="
            f"{item['oem_occurrences']}, "
            f"roles="
            f"{item['role_occurrences']}, "
            f"practical_actions="
            f"{item['practical_action_occurrences']}"
        )


def print_evidence_occurrences(
    result
):

    print()
    print("=" * 70)
    print("TECHNOLOGY EVIDENCE OCCURRENCES")
    print("=" * 70)

    for item in result.get(
        "technology_occurrences",
        []
    ):

        print()
        print(
            f"{item['normalized_name']}"
        )

        print(
            f"  Section: "
            f"{item['section']}"
        )

        print(
            f"  Evidence type: "
            f"{item['evidence_type']}"
        )

        print(
            f"  Strength: "
            f"{item['evidence_strength']}"
        )

        if item[
            "explicit_actions"
        ]:

            print(
                f"  Explicit actions: "
                f"{', '.join(item['explicit_actions'])}"
            )

        print(
            f"  Evidence: "
            f"{item['line_evidence']}"
        )