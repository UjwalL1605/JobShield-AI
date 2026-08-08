"""
Debug script for the 'screenshot of your bank balance' miss.
"""

from services.rule_engine import analyze_text

TEXT = (
    "Job confirmed! HR will call in 10 mins. Meanwhile please share a "
    "screenshot of your bank balance to verify eligibility for the WFH "
    "data entry role, this is required by our finance team."
)
result = analyze_text(TEXT)

print("=" * 60)
print("TEXT:")
print(TEXT)
print("=" * 60)
print(f"rule_score: {result['rule_score']}")
print(f"legit_indicator_count: {result['legit_indicator_count']}")
print()
print("risk_factors:")
for rf in result["risk_factors"]:
    print(f"  - category={rf['category']!r} severity={rf['severity']!r} count={rf['count']} matched={rf['matched_keywords']}")
print()
print("scam_keywords (raw matches):")
for kw in result["scam_keywords"]:
    print(f"  - {kw['keyword']!r} (category={kw['category']})")
print("=" * 60)