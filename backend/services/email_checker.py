"""
JobShield AI — Email Checker Service

Extracts and validates email addresses from text.
Detects free email providers impersonating corporate addresses.
"""

import re
from typing import List, Dict


# Well-known free email providers
FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "yahoo.in", "yahoo.co.in",
    "outlook.com", "hotmail.com", "live.com", "live.in",
    "rediffmail.com", "mail.com", "protonmail.com",
    "aol.com", "zoho.com", "yandex.com",
    "icloud.com", "gmx.com", "fastmail.com",
    "inbox.com", "tutanota.com", "guerrillamail.com",
}

# Known company name patterns that indicate impersonation
COMPANY_NAMES = [
    "google", "microsoft", "amazon", "apple", "meta", "facebook",
    "tcs", "infosys", "wipro", "hcl", "cognizant", "capgemini",
    "flipkart", "paytm", "razorpay", "phonepe", "swiggy", "zomato",
    "reliance", "tata", "mahindra", "adani", "byju", "unacademy",
    "deloitte", "kpmg", "accenture", "ibm", "oracle", "sap",
    "salesforce", "adobe", "nvidia", "tesla", "uber", "ola",
    "jpmogan", "goldman", "morgan stanley", "deutsche",
]

# Known corporate domains for major companies
KNOWN_CORPORATE_DOMAINS = {
    "google": ["google.com", "google.co.in"],
    "microsoft": ["microsoft.com", "outlook.com"],
    "amazon": ["amazon.com", "amazon.in"],
    "tcs": ["tcs.com"],
    "infosys": ["infosys.com"],
    "wipro": ["wipro.com"],
    "flipkart": ["flipkart.com"],
    "paytm": ["paytm.com"],
    "accenture": ["accenture.com"],
    "deloitte": ["deloitte.com"],
    "ibm": ["ibm.com"],
    "oracle": ["oracle.com"],
    "cognizant": ["cognizant.com"],
    "capgemini": ["capgemini.com"],
}


def extract_emails(text: str) -> List[str]:
    """Extract all email addresses from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return list(set(re.findall(pattern, text)))


def check_email(email: str) -> Dict:
    """
    Analyze a single email address for legitimacy.

    Returns:
        Dict with risk_level, reasons, and details.
    """
    email_lower = email.lower()
    local_part, domain = email_lower.rsplit("@", 1)

    result = {
        "email": email,
        "domain": domain,
        "is_free_provider": domain in FREE_PROVIDERS,
        "risk_level": "low",
        "reasons": [],
    }

    # Check if using free provider
    if domain in FREE_PROVIDERS:
        result["reasons"].append(
            f"Uses free email provider ({domain}). Legitimate companies use corporate domains."
        )
        result["risk_level"] = "medium"

        # Check if local part contains company names (impersonation)
        for company in COMPANY_NAMES:
            if company in local_part:
                result["reasons"].append(
                    f"Email claims affiliation with '{company}' but uses {domain} — "
                    f"likely impersonation. Official {company} emails use @{company}.com"
                )
                result["risk_level"] = "high"
                break

        # Check for HR/recruitment patterns on free email
        hr_patterns = ["hr", "hiring", "recruit", "career", "placement", "jobs"]
        for pattern in hr_patterns:
            if pattern in local_part:
                result["reasons"].append(
                    f"HR/recruitment email using free provider ({domain}) is suspicious."
                )
                if result["risk_level"] != "high":
                    result["risk_level"] = "high"
                break
    else:
        # Check if domain is known corporate
        for company, domains in KNOWN_CORPORATE_DOMAINS.items():
            if domain in domains:
                result["reasons"].append(
                    f"Email is from known corporate domain ({domain}). ✓"
                )
                result["risk_level"] = "low"
                return result

        # Unknown domain — neutral
        result["reasons"].append(
            f"Email domain ({domain}) is not a known free provider."
        )

    return result


def analyze_emails_in_text(text: str) -> Dict:
    """
    Extract and analyze all emails found in the text.

    Returns:
        Dict with list of email analyses and overall risk.
    """
    emails = extract_emails(text)

    if not emails:
        return {
            "emails_found": 0,
            "analyses": [],
            "overall_risk": "unknown",
        }

    analyses = [check_email(email) for email in emails]

    # Overall risk is the max risk across all emails
    risk_order = {"low": 0, "medium": 1, "high": 2}
    max_risk = max(analyses, key=lambda x: risk_order.get(x["risk_level"], 0))

    return {
        "emails_found": len(emails),
        "analyses": analyses,
        "overall_risk": max_risk["risk_level"],
    }
