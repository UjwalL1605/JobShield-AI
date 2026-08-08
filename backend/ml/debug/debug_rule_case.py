"""
Quick debug script - run this from your backend/ folder to see exactly
what the rule engine detects (or misses) for the low-scoring case.
"""

from services.rule_engine import analyze_text

TEXT = (
    "Selected for the internship! Please note this program does involve "
    "a nominal training material fee of Rs 299 which covers your certificate "
    "and course access, standard for all our cohorts."
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