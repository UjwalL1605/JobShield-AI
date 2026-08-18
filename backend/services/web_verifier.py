"""
JobShield AI — Web Intelligence & Entity Verifier

Extracts entities (companies, domains, emails, phones, Telegram handles, UPI IDs)
and performs domain reputation checks, brand impersonation detection, and
generates targeted Google Search threat intelligence queries.
"""

import re
import urllib.parse
from typing import Dict, List, Optional

from services.constants import (
    KNOWN_LEGIT_COMPANIES,
    HIGH_RISK_TLDS,
    URL_SHORTENERS,
    FREE_EMAIL_DOMAINS,
)


def extract_entities(text: str) -> Dict:
    """Extract companies, emails, domains, phone numbers, UPI IDs, and links from text."""
    # 1. Emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(email_pattern, text)))

    # 2. URLs and Domains
    raw_urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    domains = set()
    for u in raw_urls:
        m = re.search(r'^(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', u)
        if m:
            domains.add(m.group(1).lower())

    # Bare domain mentions (e.g., "careers-portal.site")
    bare_domains = re.findall(r'\b([a-zA-Z0-9-]+\.(?:com|in|net|org|site|online|xyz|top|info|work|live|co))\b', text.lower())
    for bd in bare_domains:
        domains.add(bd)

    # 3. Phone Numbers (Indian format + global)
    phone_pattern = r'(?:\+?91[-\s]?)?[6-9]\d{9}\b'
    phones = list(set(re.findall(phone_pattern, text)))

    # 4. Telegram & WhatsApp Links / Handles
    telegram_handles = list(set(re.findall(r'(?:t\.me/|telegram\.me/|@)([a-zA-Z0-9_]{4,32})\b', text, re.IGNORECASE)))
    whatsapp_links = list(set(re.findall(r'(?:wa\.me/|chat\.whatsapp\.com/|api\.whatsapp\.com/send\?phone=)(\+?[0-9a-zA-Z]+)', text, re.IGNORECASE)))

    # 5. UPI Handles
    upi_pattern = r'\b([a-zA-Z0-9._-]+@(paytm|gpay|okaxis|okicici|okhdfcbank|oksbi|ybl|axl|ibl|upi|apl))\b'
    upis = [m[0] for m in re.findall(upi_pattern, text, re.IGNORECASE)]

    # 6. Company Names Detection
    detected_companies = []
    text_lower = text.lower()

    for comp_key in KNOWN_LEGIT_COMPANIES:
        if re.search(rf'\b{re.escape(comp_key)}\b', text_lower):
            detected_companies.append(comp_key.title())

    # Generic company name extraction heuristic ("at <Company>", "from <Company> HR")
    hr_comp_match = re.findall(r'(?:at|from|with|hiring\s+for|recruitment\s+at)\s+([A-Z][a-zA-Z0-9&.,\s-]{2,25}(?:Inc|Ltd|Limited|Technologies|Solutions|Enterprises|Pvt|LLC|Pvt\.\s*Ltd\.)?)', text)
    for c in hr_comp_match:
        c_clean = c.strip(" ,.-")
        if c_clean and len(c_clean) > 2 and c_clean.lower() not in [dc.lower() for dc in detected_companies]:
            # Filter common false positives
            if c_clean.lower() not in ["our team", "home", "the final stage", "our company", "remote", "india"]:
                detected_companies.append(c_clean)

    return {
        "emails": emails,
        "domains": list(domains),
        "urls": raw_urls,
        "phones": phones,
        "telegram_handles": telegram_handles,
        "whatsapp_links": whatsapp_links,
        "upi_ids": upis,
        "companies": detected_companies,
    }


def analyze_web_intelligence(text: str, source_type: Optional[str] = None) -> Dict:
    """
    Perform deep web intelligence checks, domain risk analysis,
    brand impersonation detection, and generate live Google search queries.
    """
    entities = extract_entities(text)
    risk_signals = []
    risk_boost = 0.0
    impersonation_detected = False

    # 1. Check Brand Impersonation
    for comp in entities["companies"]:
        comp_key = comp.lower()
        if comp_key in KNOWN_LEGIT_COMPANIES:
            legit_domains = KNOWN_LEGIT_COMPANIES[comp_key]
            
            # Check if any email domain or URL domain matches the legitimate domains
            found_official = False
            for d in entities["domains"]:
                if any(d == ld or d.endswith("." + ld) for ld in legit_domains):
                    found_official = True
                    break
            
            # Check emails
            for em in entities["emails"]:
                em_domain = em.split("@")[-1].lower()
                if em_domain in FREE_EMAIL_DOMAINS:
                    risk_signals.append({
                        "type": "brand_impersonation",
                        "severity": "critical",
                        "title": f"Impersonation Alert: {comp} using free email ({em_domain})",
                        "detail": f"The message claims to represent {comp}, but uses a free public email address ({em}). Official recruiters never use free email providers.",
                    })
                    risk_boost += 25.0
                    impersonation_detected = True
                elif any(em_domain == ld or em_domain.endswith("." + ld) for ld in legit_domains):
                    found_official = True

            # If brand mentioned with only WhatsApp/Telegram contact and NO official domain
            if (entities["phones"] or entities["telegram_handles"] or source_type in ["whatsapp", "telegram"]) and not found_official:
                risk_signals.append({
                    "type": "unofficial_channel_impersonation",
                    "severity": "high",
                    "title": f"MNC Brand Impersonation: {comp} hiring via unofficial channel",
                    "detail": f"{comp} is a major firm that never conducts hiring exclusively via personal WhatsApp/Telegram or SMS without official corporate domain verification.",
                })
                risk_boost += 20.0
                impersonation_detected = True

    # 2. Check Suspicious TLDs and URL Shorteners
    for d in entities["domains"]:
        d_lower = d.lower()
        # High risk TLD
        if any(d_lower.endswith(tld) for tld in HIGH_RISK_TLDS):
            risk_signals.append({
                "type": "high_risk_domain",
                "severity": "high",
                "title": f"High-Risk Phishing TLD: {d}",
                "detail": f"The domain '{d}' uses a cheap/unregulated extension commonly associated with temporary phishing and job scam landing pages.",
            })
            risk_boost += 15.0

        # Shorteners
        if any(d_lower == shortener or d_lower.endswith("." + shortener) for shortener in URL_SHORTENERS):
            risk_signals.append({
                "type": "masked_url_shortener",
                "severity": "medium",
                "title": f"Masked URL Shortener: {d}",
                "detail": f"The link uses '{d}' to obscure the true destination URL. Scammers frequently use URL shorteners to bypass domain filters.",
            })
            risk_boost += 10.0

    # 3. Check Free Email for Generic Corporate Recruitment
    if not impersonation_detected:
        for em in entities["emails"]:
            em_domain = em.split("@")[-1].lower()
            if em_domain in FREE_EMAIL_DOMAINS:
                risk_signals.append({
                    "type": "free_recruiter_email",
                    "severity": "medium",
                    "title": f"Free Email Used for Recruitment ({em})",
                    "detail": f"Recruiter contact '{em}' is hosted on a free public provider ({em_domain}) instead of a verifiable company domain.",
                })
                risk_boost += 10.0

    # 4. Generate Live Verification Search Queries
    google_search_queries = []
    
    # Primary company query
    primary_company = entities["companies"][0] if entities["companies"] else None
    if primary_company:
        q_text = f'"{primary_company}" scam OR "fake job" OR "fraud" OR "complaint"'
        google_search_queries.append({
            "label": f"Search '{primary_company}' Scam Reports on Google",
            "query": q_text,
            "url": f"https://www.google.com/search?q={urllib.parse.quote_plus(q_text)}",
            "type": "company_check",
        })
        # MCA / LinkedIn search link
        google_search_queries.append({
            "label": f"Verify '{primary_company}' on LinkedIn / MCA Registry",
            "query": f'"{primary_company}" official website OR linkedin',
            "url": f"https://www.google.com/search?q={urllib.parse.quote_plus(primary_company + ' official careers linkedin')}",
            "type": "legitimacy_check",
        })

    # Phone number query
    for phone in entities["phones"][:2]:
        q_phone = f'"{phone}" scam OR "fraud" OR "fake recruitment"'
        google_search_queries.append({
            "label": f"Search Phone '{phone}' on Google & Truecaller",
            "query": q_phone,
            "url": f"https://www.google.com/search?q={urllib.parse.quote_plus(q_phone)}",
            "type": "phone_check",
        })

    # Domain query
    for d in entities["domains"][:2]:
        q_dom = f'"{d}" review OR "scam" OR "whois"'
        google_search_queries.append({
            "label": f"Check Domain '{d}' Online Reputation",
            "query": q_dom,
            "url": f"https://www.google.com/search?q={urllib.parse.quote_plus(q_dom)}",
            "type": "domain_check",
        })

    # Generic Fallback query if no specific entity extracted
    if not google_search_queries and len(text) > 20:
        # Take first 60 chars of text for exact snippet lookup
        snippet = " ".join(text.split()[:8])
        q_snippet = f'"{snippet}" scam OR fraud'
        google_search_queries.append({
            "label": "Search Message Snippet on Google for Prior Reports",
            "query": q_snippet,
            "url": f"https://www.google.com/search?q={urllib.parse.quote_plus(q_snippet)}",
            "type": "text_snippet_check",
        })

    # Cybercrime Portal Quick Link
    google_search_queries.append({
        "label": "National Cyber Crime Reporting Portal (cybercrime.gov.in)",
        "query": "cybercrime.gov.in",
        "url": "https://cybercrime.gov.in/",
        "type": "official_portal",
    })

    return {
        "entities": entities,
        "risk_signals": risk_signals,
        "risk_boost": min(risk_boost, 35.0),
        "google_search_queries": google_search_queries,
        "impersonation_detected": impersonation_detected,
    }
