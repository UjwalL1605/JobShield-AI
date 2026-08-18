"""
JobShield AI — Centralized Constants & Threat Intelligence Lists

Shared threat definitions, free email providers, corporate domains, and high-risk TLDs.
Centralizing these avoids DRY violations and ensures uniform detection across services.
"""

# Unified list of free/public webmail providers
FREE_EMAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "yahoo.in", "yahoo.co.in",
    "outlook.com", "hotmail.com", "live.com", "live.in",
    "rediffmail.com", "mail.com", "protonmail.com", "proton.me",
    "aol.com", "zoho.com", "zoho.in", "yandex.com",
    "icloud.com", "gmx.com", "fastmail.com", "inbox.com",
    "tutanota.com", "tutamail.com", "guerrillamail.com", "tempmail.com",
}

# Alias for backward compatibility
FREE_EMAIL_DOMAINS = FREE_EMAIL_PROVIDERS
FREE_PROVIDERS = FREE_EMAIL_PROVIDERS

# Known company patterns for detecting impersonation
COMPANY_NAMES = [
    "google", "microsoft", "amazon", "apple", "meta", "facebook",
    "tcs", "infosys", "wipro", "hcl", "cognizant", "capgemini",
    "flipkart", "paytm", "razorpay", "phonepe", "swiggy", "zomato",
    "reliance", "tata", "mahindra", "adani", "byju", "unacademy",
    "deloitte", "kpmg", "accenture", "ibm", "oracle", "sap",
    "salesforce", "adobe", "nvidia", "tesla", "uber", "ola",
    "jpmorgan", "goldman", "morgan stanley", "deutsche",
]

# Verified Official Domains for Top MNCs / Indian Employers
KNOWN_LEGIT_COMPANIES = {
    "google": ["google.com", "careers.google.com", "abc.xyz"],
    "microsoft": ["microsoft.com", "careers.microsoft.com"],
    "amazon": ["amazon.com", "amazon.jobs", "amazon.in"],
    "apple": ["apple.com", "jobs.apple.com"],
    "meta": ["meta.com", "metacareers.com", "fb.com"],
    "tcs": ["tcs.com", "careers.tcs.com", "nextstep.tcs.com"],
    "infosys": ["infosys.com", "career.infosys.com"],
    "wipro": ["wipro.com", "careers.wipro.com"],
    "hcl": ["hcltech.com", "hcl.com"],
    "tech mahindra": ["techmahindra.com"],
    "cognizant": ["cognizant.com", "careers.cognizant.com"],
    "deloitte": ["deloitte.com"],
    "kpmg": ["kpmg.com"],
    "accenture": ["accenture.com"],
    "ibm": ["ibm.com", "careers.ibm.com"],
    "oracle": ["oracle.com"],
    "capgemini": ["capgemini.com"],
    "flipkart": ["flipkart.com", "flipkartcareers.com"],
    "zomato": ["zomato.com"],
    "swiggy": ["swiggy.in"],
    "paytm": ["paytm.com"],
    "jio": ["jio.com", "ril.com"],
    "tata": ["tata.com", "tatamotors.com", "tatasteel.com"],
    "l&t": ["larsentoubro.com"],
    "hdfc": ["hdfcbank.com"],
    "icici": ["icicibank.com"],
    "sbi": ["sbi.co.in", "bank.sbi"],
}

KNOWN_CORPORATE_DOMAINS = KNOWN_LEGIT_COMPANIES

# Suspicious / Cheap TLDs heavily used in recruitment scams & phishing
HIGH_RISK_TLDS = {
    ".xyz", ".top", ".site", ".online", ".club", ".work", ".link",
    ".info", ".live", ".tk", ".ml", ".ga", ".cf", ".gq", ".buzz",
    ".icu", ".monster", ".uno", ".cc", ".fun", ".rest",
}

# Known URL Shorteners that mask the true destination
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "is.gd", "cutt.ly", "rb.gy", "shorturl.at",
    "t.co", "ow.ly", "buff.ly", "adf.ly", "goo.gl",
}
