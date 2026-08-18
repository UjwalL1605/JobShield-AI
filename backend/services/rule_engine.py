"""
JobShield AI — Rule-Based Scam Detection Engine

Identifies scam indicators using pattern matching, keyword detection,
and heuristic rules. Returns risk factors with severity levels.
"""

import re
from typing import List, Dict, Tuple


# ─── Scam Keyword Categories ────────────────────────────────────────────────────

SCAM_KEYWORDS = {
    "fee_request": {
        "severity": "high",
        "description": "Payment or fee request detected",
        "keywords": [
            # Explicit symbol-based
            "registration fee", "processing fee", "security deposit",
            "training fee", "admission fee", "application fee",
            "verification fee", "exam fee", "one-time fee",
            "pay ₹", "pay rs", "pay inr", "transfer ₹",
            "deposit ₹", "deposit rs", "membership fee",
            "joining fee", "onboarding fee", "background verification fee",
            "pay to confirm", "pay to register", "pay to start",
            "fee of ₹", "fee of rs", "charge of ₹",
            "training material fee", "course material fee", "material fee",
            "certificate fee", "certification fee", "platform fee",
            # Additional fee types (no ₹ required)
            "hr processing fee", "documentation fee", "documentation charge",
            "verification charge", "document verification fee",
            "onboarding fee", "background check fee",
            "security fee", "slot booking fee",
            "enrollment fee", "enrollment cost", "training enrollment",
            "appointment letter fee", "appointment fee",
            "id generation fee", "id card fee",
            # Refund promise (classic scam tactic)
            "refundable deposit", "fully refundable", "completely refundable",
            "refunded with your first salary", "refunded with first month",
            "adjusted against your first", "adjusted against first month",
            "deducted from first salary", "deducted from salary",
            "documentation and verification", "verification and documentation",
            "background verification process", "employee verification process",
            # Generic pay + amount patterns handled by regex (see below)
            "please pay", "you must pay", "need to pay", "required to pay",
            "make payment", "complete payment", "complete the payment",
            "pay before", "payment must be", "payment is required",
            "total cost is", "total amount is", "fees to be paid",
        ],
    },
    "urgency_language": {
        "severity": "medium",
        "description": "Urgency or pressure tactics detected",
        "keywords": [
            "limited seats", "offer expires", "act now",
            "hurry", "last chance", "final call",
            "immediately", "within 24 hours", "within 2 hours",
            "within 48 hours", "within 12 hours", "within 6 hours",
            "don't miss", "limited time", "only today",
            "before all positions", "seats left", "expires today",
            "apply now before", "urgent hiring", "urgent requirement",
            "quick hiring", "instant joining", "immediate joining",
            "valid for only 24 hours", "valid for only 48 hours",
            "before 6:00 pm", "before 6 pm", "before today",
            "finalize your joining", "avoid cancellation",
            "offer will be cancelled", "offer will expire",
        ],
    },
    "guaranteed_outcomes": {
        "severity": "high",
        "description": "Unrealistic guarantees or no-interview selection detected",
        "keywords": [
            "guaranteed placement", "100% placement", "guaranteed job",
            "guaranteed returns", "guaranteed income", "100% guaranteed",
            "assured placement", "sure shot", "confirm your seat",
            "guaranteed selection", "no interview required",
            "no technical interview", "no further interview",
            "no experience needed", "no skills required",
            "no qualification needed", "no resume needed",
            # Selection without process
            "selected based on your online profile",
            "selected from our candidate database",
            "selected from our database",
            "selection has been completed",
            "shortlisted based on your resume",
            "profile has been selected",
            "your profile was selected",
            # 'No interview' variants (with/without 'is')
            "no interview is required",
            "no further interview is required",
            "no technical interview is required",
            "without any interview",
            "no rounds of interview",
            "skip the interview",
        ],
    },
    "payment_methods": {
        "severity": "high",
        "description": "Direct payment method mentioned",
        "keywords": [
            "@paytm", "@gpay", "@phonepe", "@upi",
            "upi id", "upi:", "google pay", "phonepe",
            "paytm", "bhim", "bank transfer",
            "send money", "transfer amount",
        ],
    },
    "suspicious_communication": {
        "severity": "medium",
        "description": "Unprofessional communication channel",
        "keywords": [
            "whatsapp", "telegram", "dm us", "dm now",
            "contact on whatsapp", "join our channel",
            "instagram @", "dm on instagram",
            "message us on", "ping us on",
        ],
    },
    "unrealistic_claims": {
        "severity": "medium",
        "description": "Unrealistic job claims detected",
        "keywords": [
            "work from home", "work from anywhere", "wfh",
            "earn from home", "simple typing work",
            "data entry operators", "data entry", "copy paste work",
            "free laptop", "passive income",
            "unlimited income", "earn daily",
            "flexible hours", "part time earn",
        ],
    },
    "emotional_manipulation": {
        "severity": "medium",
        "description": "Emotional manipulation language",
        "keywords": [
            "congratulations!", "you have been selected",
            "you are shortlisted", "you won", "lottery selection",
            "golden opportunity", "dream job", "exciting opportunity!",
            "selected for", "been chosen", "lucky candidate",
            "🎉", "🌟", "⚠️",
        ],
    },
    "impersonation_signals": {
        "severity": "high",
        "description": "Possible company impersonation",
        "keywords": [
            "google/microsoft", "tcs/infosys", "microsoft/amazon",
            "wipro/tcs", "found your resume on naukri",
            "found your profile on", "i am hr from",
            "this is from hr", "walk-in drive",
        ],
    },
    "referral_scheme": {
        "severity": "high",
        "description": "Multi-level or referral scheme detected",
        "keywords": [
            "refer friends", "each referral earns",
            "referral bonus", "affiliate program",
            "invest and earn", "invest ₹", "invest rs",
            "returns guaranteed", "daily returns",
            "membership fee", "joining package",
        ],
    },
    "credential_harvesting": {
        "severity": "high",
        "description": "Request for sensitive personal/banking credentials",
        "keywords": [
            "bank login", "bank account number", "otp", "upi pin",
            "aadhaar number", "aadhaar card", "pan card", "ifsc code",
            "bank passbook", "date of birth and address", "screenshot of your bank",
            "share your bank", "kyc is pending", "complete your kyc",
            "verify your identity by sharing", "banking details for",
            "send the transaction screenshot", "send payment screenshot",
            "payment confirmation", "send aadhaar", "send pan card",
        ],
    },
    "investment_scam": {
        "severity": "high",
        "description": "Investment or task-based earning scheme detected",
        "keywords": [
            "guaranteed returns", "trading assistant", "crypto trading",
            "task group", "complete simple tasks", "task assignments",
            "starting investment", "open your trading account",
            "weekly returns", "unlock higher paying tasks",
        ],
    },
    "fake_selection_process": {
        "severity": "high",
        "description": "Fraudulent selection or offer letter process detected",
        "keywords": [
            "appointment letter", "offer letter will be generated",
            "employee id will be generated", "generate your appointment",
            "joining letter", "generate your offer letter",
            "your selection is confirmed", "your seat is confirmed",
            "reserve your internship seat", "reserve your seat",
            "activate your internship account", "activate your account",
            "fast-track hiring", "fast track hiring",
            "no technical round", "no aptitude test",
            "direct selection", "direct joining",
        ],
    },
}

# ─── Legitimate Indicators ──────────────────────────────────────────────────────

LEGIT_INDICATORS = {
    "professional_process": [
        "technical interview", "coding test", "hr discussion",
        "resume screening", "aptitude test", "group discussion",
        "we do not charge", "no fees required", "no registration charges",
        "no registration fee", "equal opportunity employer",
    ],
    "specific_requirements": [
        "years of experience", "years experience",
        "qualifications:", "requirements:", "responsibilities:",
        "skills required", "eligibility:", "minimum qualification",
    ],
    "formal_language": [
        "we are pleased", "thank you for applying",
        "we have reviewed", "after careful consideration",
        "we regret to inform", "competitive salary",
        "health insurance", "learning budget",
    ],
    "proper_channels": [
        "careers page", "apply online", "placement portal",
        "apply through", "apply at https",
    ],
}

# ─── Free Email Providers ───────────────────────────────────────────────────────

FREE_EMAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "yahoo.in", "yahoo.co.in",
    "outlook.com", "hotmail.com", "live.com",
    "rediffmail.com", "mail.com", "protonmail.com",
    "aol.com", "zoho.com", "yandex.com",
    "icloud.com", "gmx.com", "fastmail.com",
}

# ─── Negation Handling ──────────────────────────────────────────────────────────

NEGATION_WORDS = {
    "no", "not", "without", "never", "none", "n't",
    "does not", "doesn't", "do not", "don't",
    "did not", "didn't", "won't", "will not",
    "free of", "waived", "exempt from",
}

# Categories where a preceding negation flips the meaning (fee/payment/guarantee
# claims). Urgency and emotional-manipulation language isn't meaningfully
# negatable the same way, so we leave those categories alone.
NEGATABLE_CATEGORIES = {"fee_request", "guaranteed_outcomes", "payment_methods", "referral_scheme"}


def _is_negated(text_lower: str, match_start: int, window_chars: int = 30) -> bool:
    """
    Check if a matched keyword is preceded by a negation word within a
    short window (e.g. 'no registration fee', 'does not require payment').
    Looks backward from the match position, not forward, since negation
    almost always precedes the thing being negated in English.
    """
    window_start = max(0, match_start - window_chars)
    preceding_text = text_lower[window_start:match_start]

    for neg in NEGATION_WORDS:
        pattern = r'\b' + re.escape(neg) + r'\b'
        if re.search(pattern, preceding_text):
            return True
    return False

# ─── Regex Patterns for Amount-Based Fee Detection ──────────────────────────────
# Catches "pay a 1499", "paying 2250", "cost is 1200", "fee of 999" etc.
# even when no ₹/Rs symbol is present (common in informal scam emails).
_AMOUNT_FEE_PATTERNS = [
    # "pay a 999", "pay 1499", "paying 2250", "pay a 1750"
    re.compile(r'\bpay(?:ing)?\s+(?:a\s+)?(?:rs\.?\s*|₹\s*|inr\s*)?[1-9][\d,]{2,}\b', re.I),
    # "fee of 999", "fee of rs 2250", "fees of 1499"
    re.compile(r'\bfees?\s+(?:of\s+)?(?:rs\.?\s*|₹\s*|inr\s*)?[1-9][\d,]{2,}\b', re.I),
    # "charge of 1750", "charges of 500"
    re.compile(r'\bcharges?\s+(?:of\s+)?(?:rs\.?\s*|₹\s*|inr\s*)?[1-9][\d,]{2,}\b', re.I),
    # "cost is 1200", "total cost is 799", "cost of 999"
    re.compile(r'\bcost\s+(?:is\s+|of\s+)?(?:rs\.?\s*|₹\s*|inr\s*)?[1-9][\d,]{2,}\b', re.I),
    # "deposit of 999", "deposit 1499", "a 999 deposit"
    re.compile(r'\bdeposit\s+(?:of\s+)?(?:rs\.?\s*|₹\s*|inr\s*)?[1-9][\d,]{2,}\b', re.I),
    re.compile(r'\b(?:a\s+)?(?:rs\.?\s*|₹\s*|inr\s*)?[1-9][\d,]{2,}\s+(?:refundable\s+)?(?:security\s+)?deposit\b', re.I),
    # "amount is 2250", "amount of 799"
    re.compile(r'\bamount\s+(?:is\s+|of\s+)?(?:rs\.?\s*|₹\s*|inr\s*)?[1-9][\d,]{2,}\b', re.I),
    # "a ₹999", "a Rs 1499" (amount after article)
    re.compile(r'\ba\s+(?:rs\.?\s*|₹\s*|inr\s*)[1-9][\d,]{2,}\b', re.I),
]


def analyze_text(text: str) -> Dict:
    """
    Run rule-based scam analysis on text.

    Returns:
        Dict with risk_factors, scam_keywords, legit_indicators,
        rule_score (0-100), and highlighted_keywords.
    """
    text_lower = text.lower()
    risk_factors = []
    found_keywords = []
    legit_count = 0

    # ── Check scam keyword categories (negation-aware) ──────────────────────
    negated_matches_count = 0

    for category, info in SCAM_KEYWORDS.items():
        matched = []
        for keyword in info["keywords"]:
            if keyword.lower() not in text_lower:
                continue

            for m in re.finditer(re.escape(keyword.lower()), text_lower):
                if category in NEGATABLE_CATEGORIES and _is_negated(text_lower, m.start()):
                    # "no registration fee" — skip this occurrence, it's not a risk signal
                    negated_matches_count += 1
                    continue

                matched.append(keyword)
                found_keywords.append({
                    "keyword": text[m.start():m.end()],
                    "start": m.start(),
                    "end": m.end(),
                    "category": category,
                    "severity": info["severity"],
                })

        if matched:
            risk_factors.append({
                "category": category,
                "severity": info["severity"],
                "description": info["description"],
                "matched_keywords": matched,
                "count": len(matched),
            })

    # ── Regex-based amount fee detection (no ₹ symbol required) ─────────────
    amount_matches = []
    for pattern in _AMOUNT_FEE_PATTERNS:
        for m in pattern.finditer(text):
            matched_text = m.group()
            # Respect negation: "no fee of 999", "without any payment"
            if not _is_negated(text_lower, m.start(), window_chars=40):
                amount_matches.append(matched_text)
                found_keywords.append({
                    "keyword": matched_text,
                    "start": m.start(),
                    "end": m.end(),
                    "category": "fee_request",
                    "severity": "high",
                })

    # Deduplicate and group amount matches as a risk factor
    if amount_matches:
        # Check if fee_request already has a risk factor entry
        existing = next((r for r in risk_factors if r["category"] == "fee_request"), None)
        if existing:
            existing["matched_keywords"].extend(amount_matches)
            existing["count"] += len(amount_matches)
        else:
            risk_factors.append({
                "category": "fee_request",
                "severity": "high",
                "description": "Payment amount request detected (without currency symbol)",
                "matched_keywords": amount_matches,
                "count": len(amount_matches),
            })

    # ── Check legitimate indicators ──────────────────────────────────────────
    for category, phrases in LEGIT_INDICATORS.items():
        for phrase in phrases:
            if phrase.lower() in text_lower:
                legit_count += 1

    # ── Email analysis ───────────────────────────────────────────────────────
    email_risks = _analyze_emails(text)
    risk_factors.extend(email_risks)

    # ── URL analysis ─────────────────────────────────────────────────────────
    url_risks = _analyze_urls(text)
    risk_factors.extend(url_risks)

    # ── Salary analysis ──────────────────────────────────────────────────────
    salary_risks = _analyze_salary(text)
    risk_factors.extend(salary_risks)

    # ── Negated scam claims ("no fee", "no registration charge") count as a
    #    mild legitimacy signal — explicitly disclaiming a fee is a real
    #    pattern legitimate recruiters use. ──────────────────────────────────
    legit_count += min(negated_matches_count, 3)  # cap contribution

    # ── Calculate rule-based score ───────────────────────────────────────────
    rule_score = _calculate_score(risk_factors, legit_count)

    # ── Deduplicate and sort keywords ────────────────────────────────────────
    seen_positions = set()
    unique_keywords = []
    for kw in found_keywords:
        pos_key = (kw["start"], kw["end"])
        if pos_key not in seen_positions:
            seen_positions.add(pos_key)
            unique_keywords.append(kw)
    unique_keywords.sort(key=lambda x: x["start"])

    return {
        "risk_factors": risk_factors,
        "scam_keywords": unique_keywords,
        "legit_indicator_count": legit_count,
        "rule_score": rule_score,
    }


def _analyze_emails(text: str) -> List[Dict]:
    """Extract and analyze email addresses in text."""
    risks = []
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)

    for email in emails:
        domain = email.split("@")[1].lower()
        local_part = email.split("@")[0].lower()

        if domain in FREE_EMAIL_PROVIDERS:
            # Check if it claims to be from a company
            company_indicators = [
                "hr", "hiring", "recruit", "career", "placement",
                "job", "google", "microsoft", "amazon", "tcs",
                "infosys", "wipro", "flipkart", "paytm",
            ]
            is_company_claim = any(ind in local_part for ind in company_indicators)

            if is_company_claim:
                risks.append({
                    "category": "unofficial_email",
                    "severity": "high",
                    "description": f"Unofficial email domain: '{email}' uses free provider ({domain}) while claiming corporate affiliation",
                    "matched_keywords": [email],
                    "count": 1,
                })
            else:
                risks.append({
                    "category": "free_email",
                    "severity": "medium",
                    "description": f"Free email provider used: '{email}' — legitimate companies typically use corporate domains",
                    "matched_keywords": [email],
                    "count": 1,
                })

    return risks


def _analyze_urls(text: str) -> List[Dict]:
    """Extract and analyze URLs in text."""
    risks = []
    url_pattern = r'https?://[^\s<>\"\')\]]+|www\.[^\s<>\"\')\]]+'
    urls = re.findall(url_pattern, text)

    suspicious_tlds = {".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".buzz", ".click"}
    suspicious_patterns = ["career", "job", "hire", "recruit", "placement"]

    for url in urls:
        url_lower = url.lower()

        # Check suspicious TLDs
        for tld in suspicious_tlds:
            if url_lower.endswith(tld) or (tld + "/") in url_lower:
                risks.append({
                    "category": "suspicious_url",
                    "severity": "high",
                    "description": f"Suspicious domain TLD: '{url}' uses unusual extension ({tld})",
                    "matched_keywords": [url],
                    "count": 1,
                })
                break

        # Check for company name in non-official domain
        if not url_lower.startswith("https://"):
            risks.append({
                "category": "insecure_url",
                "severity": "medium",
                "description": f"Non-HTTPS URL detected: '{url}'",
                "matched_keywords": [url],
                "count": 1,
            })

    return risks


def _analyze_salary(text: str) -> List[Dict]:
    """Detect and validate salary claims."""
    risks = []
    text_lower = text.lower()

    # Match salary patterns: ₹X,XX,XXX or Rs.X,XX,XXX
    salary_patterns = [
        r'₹\s?[\d,]+(?:/(?:month|day|hr|hour))?',
        r'rs\.?\s?[\d,]+(?:/(?:month|day|hr|hour))?',
        r'inr\s?[\d,]+(?:/(?:month|day|hr|hour))?',
        r'[\d,]+\s?(?:lpa|per annum|per month|/month|/day)',
    ]

    for pattern in salary_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            # Extract numeric value
            numbers = re.findall(r'[\d,]+', match)
            if numbers:
                try:
                    value = int(numbers[0].replace(",", ""))
                except ValueError:
                    continue

                # Heuristic: check if salary seems unrealistic
                is_monthly = any(w in match for w in ["/month", "per month"])
                is_daily = any(w in match for w in ["/day", "per day"])

                if is_monthly and value > 100000:
                    # Check for experience/qualification context
                    no_exp_indicators = [
                        "fresher", "no experience", "10th pass", "12th pass",
                        "no skills", "no qualification", "entry level",
                        "work from home", "data entry", "typing",
                    ]
                    if any(ind in text_lower for ind in no_exp_indicators):
                        risks.append({
                            "category": "unrealistic_salary",
                            "severity": "high",
                            "description": f"Unrealistically high salary ({match}) for entry-level/no-experience role",
                            "matched_keywords": [match],
                            "count": 1,
                        })

                if is_daily and value > 5000:
                    risks.append({
                        "category": "unrealistic_salary",
                        "severity": "high",
                        "description": f"Unusually high daily wage ({match}) — likely too good to be true",
                        "matched_keywords": [match],
                        "count": 1,
                    })

    return risks


def _calculate_score(risk_factors: List[Dict], legit_count: int) -> float:
    """Calculate overall rule-based scam score (0-100)."""
    score = 0.0

    severity_weights = {
        "high": 18,
        "medium": 10,
        "low": 5,
    }

    for factor in risk_factors:
        weight = severity_weights.get(factor["severity"], 5)
        count_multiplier = min(factor.get("count", 1), 3)  # Cap at 3
        score += weight * (1 + 0.3 * (count_multiplier - 1))

    # Reduce score for legitimate indicators
    score -= legit_count * 8

    # Clamp to 0-100
    return max(0.0, min(100.0, score))


def get_trust_level(score: float) -> str:
    """Convert scam probability to trust level label."""
    if score < 25:
        return "Safe"
    elif score < 45:
        return "Likely Safe"
    elif score < 62:
        return "Suspicious"
    elif score < 78:
        return "High Risk"
    else:
        return "Very High Risk"