"""
JobShield AI — Salary Checker Service

Extracts salary claims from text and validates them against
realistic benchmarks based on context (role, experience, work type).
"""

import re
from typing import List, Dict, Optional


# ─── Salary Benchmarks (INR Monthly) ────────────────────────────────────────────

SALARY_BENCHMARKS = {
    "fresher": {"min": 10000, "max": 60000, "label": "Fresher / Entry Level"},
    "intern": {"min": 5000, "max": 40000, "label": "Internship"},
    "data_entry": {"min": 8000, "max": 25000, "label": "Data Entry"},
    "typing": {"min": 5000, "max": 18000, "label": "Typing / Copy-Paste"},
    "work_from_home": {"min": 10000, "max": 50000, "label": "Work From Home (Entry)"},
    "experienced": {"min": 30000, "max": 300000, "label": "Experienced Professional"},
}

# Context keywords that help determine the role level
CONTEXT_INDICATORS = {
    "no_experience": [
        "no experience", "fresher", "freshers", "fresh graduate",
        "no skills required", "no qualification", "anyone can apply",
        "10th pass", "12th pass", "no degree",
    ],
    "entry_level": [
        "entry level", "junior", "trainee", "graduate",
        "intern", "internship", "stipend",
    ],
    "data_entry": [
        "data entry", "typing work", "copy paste", "form filling",
        "simple typing", "typing job",
    ],
    "work_from_home": [
        "work from home", "wfh", "work from anywhere",
        "remote work", "earn from home", "home based",
    ],
    "part_time": [
        "part time", "part-time", "flexible hours",
        "few hours", "spare time",
    ],
}


def extract_salary_amounts(text: str) -> List[Dict]:
    """
    Extract salary/payment amounts from text with context.

    Returns list of dicts with value, currency, period, and raw_match.
    """
    text_lower = text.lower()
    amounts = []

    patterns = [
        # ₹X,XX,XXX/month
        (r'₹\s?([\d,]+)\s*/?(?:per\s*)?(month|day|hr|hour|week|year|annum)',
         "INR"),
        # Rs. X,XX,XXX/month
        (r'rs\.?\s?([\d,]+)\s*/?(?:per\s*)?(month|day|hr|hour|week|year|annum)',
         "INR"),
        # INR X,XX,XXX
        (r'inr\s?([\d,]+)\s*/?(?:per\s*)?(month|day|hr|hour|week|year|annum)?',
         "INR"),
        # X LPA
        (r'([\d.]+)\s*(?:lpa|lakhs?\s*per\s*annum|lakh\s*pa)',
         "LPA"),
        # X,XX,XXX/month (without currency symbol)
        (r'salary[:\s]+([\d,]+)\s*/?(?:per\s*)?(month|day)',
         "INR"),
        # Stipend: X,XXX
        (r'stipend[:\s]+₹?\s?([\d,]+)',
         "INR"),
    ]

    for pattern, currency in patterns:
        for match in re.finditer(pattern, text_lower):
            try:
                value_str = match.group(1).replace(",", "")
                value = float(value_str)

                period = match.group(2) if match.lastindex >= 2 and match.group(2) else "month"

                # Normalize to monthly
                if currency == "LPA":
                    monthly_value = value * 100000 / 12
                    period = "month"
                elif period in ("year", "annum"):
                    monthly_value = value / 12
                elif period == "day":
                    monthly_value = value * 26  # ~26 working days
                elif period == "week":
                    monthly_value = value * 4.3
                elif period in ("hr", "hour"):
                    monthly_value = value * 8 * 26
                else:
                    monthly_value = value

                amounts.append({
                    "raw_match": match.group(0),
                    "value": value,
                    "monthly_value": monthly_value,
                    "currency": currency,
                    "period": period,
                })
            except (ValueError, IndexError):
                continue

    return amounts


def check_salary(text: str) -> Dict:
    """
    Analyze salary claims in text for plausibility.

    Returns:
        Dict with salary_found, amounts, risk_assessment, and reasons.
    """
    amounts = extract_salary_amounts(text)
    text_lower = text.lower()

    if not amounts:
        return {
            "salary_found": False,
            "amounts": [],
            "risk_level": "unknown",
            "reasons": [],
        }

    # Determine context
    context = _determine_context(text_lower)
    reasons = []
    risk_level = "low"

    for amt in amounts:
        monthly = amt["monthly_value"]

        # Check against benchmarks for detected context
        for ctx in context:
            benchmark = SALARY_BENCHMARKS.get(ctx)
            if benchmark:
                if monthly > benchmark["max"] * 2:
                    reasons.append(
                        f"Salary {amt['raw_match']} (~₹{monthly:,.0f}/month) is "
                        f"extremely high for {benchmark['label']} "
                        f"(typical range: ₹{benchmark['min']:,}–₹{benchmark['max']:,}/month)"
                    )
                    risk_level = "high"
                elif monthly > benchmark["max"] * 1.3:
                    reasons.append(
                        f"Salary {amt['raw_match']} (~₹{monthly:,.0f}/month) appears "
                        f"above market rate for {benchmark['label']}"
                    )
                    if risk_level != "high":
                        risk_level = "medium"

        # Universal red flags
        if monthly > 200000 and any(
            ind in text_lower for ind in CONTEXT_INDICATORS["no_experience"]
        ):
            reasons.append(
                f"₹{monthly:,.0f}/month for a no-experience role is "
                f"unrealistically high — strong scam indicator"
            )
            risk_level = "high"

        if amt["period"] == "day" and amt["value"] > 3000:
            reasons.append(
                f"Daily wage of {amt['raw_match']} is unusually high"
            )
            risk_level = "high"

    return {
        "salary_found": True,
        "amounts": amounts,
        "context": context,
        "risk_level": risk_level,
        "reasons": reasons,
    }


def _determine_context(text: str) -> List[str]:
    """Determine the job context from text."""
    contexts = []
    for ctx_name, keywords in CONTEXT_INDICATORS.items():
        if any(kw in text for kw in keywords):
            contexts.append(ctx_name)

    if not contexts:
        contexts.append("experienced")  # Default assumption

    return contexts
