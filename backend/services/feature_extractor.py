"""
JobShield AI — Domain Feature Extractor (v2)

Extracts explicit linguistic, structural, and domain signals for job scam detection.
Compatible with scikit-learn Pipeline and FeatureUnion.
"""

import re
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class ScamDomainFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extracts explicit domain indicators from job/message texts."""

    FEATURE_NAMES = [
        "domain:fee_payment_cue",
        "domain:advance_money_cue",
        "domain:refundable_security_cue",
        "domain:kyc_credential_harvest",
        "domain:urgency_scarcity_pressure",
        "domain:offplatform_contact_redirect",
        "domain:unrealistic_guarantee",
        "domain:investment_crypto_task_cue",
        "domain:legitimacy_safeguard",
        "domain:caps_ratio",
        "domain:exclamation_frequency",
        "domain:currency_symbol_count",
        "domain:digit_density",
    ]

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def get_feature_names_out(self, input_features=None):
        return np.array(self.FEATURE_NAMES)

    def transform(self, X):
        features = []
        for text in X:
            t = str(text).lower()
            orig = str(text)

            # 1. Fee / payment indicators
            fee_cues = bool(re.search(
                r"(registration|processing|security|training|admission|application|interview|activation|caution|verification|platform|courier|uniform|kit|listing|service|material|onboarding|facilitation)\s+(fee|charge|charges|deposit|amount|money|cost)",
                t
            )) or bool(re.search(r"(fee|charge|charges|deposit)\s+(of\s+)?(₹|rs\.?|inr|\$)?\s*\d+", t))

            pay_advance = bool(re.search(
                r"(pay|deposit|transfer|send|remit|recharge)\s+(₹|rs\.?|inr|\$)?\s*\d+",
                t
            ))

            refundable = bool(re.search(
                r"(refundable|100%\s*refund|caution\s*money|security\s*deposit|trust\s*fee|interview\s*booking\s*fee)",
                t
            ))

            # 2. Credential / KYC harvesting
            kyc_harvest = bool(re.search(
                r"(aadhaar|aadhar|pan\s*card|bank\s*account|passbook|ifsc|otp|atm\s*pin|upi\s*pin|net\s*banking|login\s*credential|user\s*id|bank\s*login|selfie\s*holding)",
                t
            ))

            # 3. Urgency / Scarcity cues
            urgency = bool(re.search(
                r"(urgent|immediately|limited\s*seats|limited\s*slots|expires\s*today|within\s*\d+\s*(hours?|mins?)|last\s*chance|hurry|final\s*call|act\s*now)",
                t
            ))

            # 4. Off-platform contact redirection
            off_platform = bool(re.search(
                r"(whatsapp|telegram|dm\s+us|dm\s+now|inbox|bit\.ly|tinyurl|t\.me|wa\.me|link\s+in\s+bio|dm\s+for\s+details)",
                t
            ))

            # 5. Guaranteed / Unreal promises
            unreal_promise = bool(re.search(
                r"(100%\s*placement|guaranteed\s*(placement|salary|returns|daily|income|trade|payout)|no\s*interview|no\s*skills|earn\s*(up\s*to\s*)?(₹|rs\.?|inr|\$)?\s*\d+\s*(per\s*day|daily|/day|/month|monthly)|simple\s*typing|lottery\s*selection|picked\s*for\s*our\s*exclusive)",
                t
            ))

            # 6. Investment / Crypto / Task Scam indicators
            investment_task = bool(re.search(
                r"(crypto|forex|trading\s*assistant|trading\s*account|signals\s*group|daily\s*returns|starting\s*investment|partner\s*exchange|like\s*videos|rating\s*apps|recharge\s*of|unlock\s*task|unlock\s*higher|withdraw\s*earnings|daily\s*withdrawal)",
                t
            ))

            # 7. Legitimacy indicators (dampeners)
            legit_cues = bool(re.search(
                r"(no\s*fees?|no\s*registration\s*fee|we\s*do\s*not\s*charge|no\s*advance\s*needed|no\s*fees\s*at\s*any\s*stage|equal\s*opportunity|benefits|health\s*insurance|provident\s*fund|\bpf\b|notice\s*period|ctc\s*:\s*\d+\s*lpa|careers\s*page|screening|interview\s*scheduled)",
                t
            ))

            # 8. Structural & Stylometric cues
            caps_ratio = sum(1 for c in orig if c.isupper()) / max(1, len(orig))
            exclamation_count = orig.count("!")
            currency_count = orig.count("₹") + orig.count("$") + t.count("rs") + t.count("inr")
            digit_count = sum(1 for c in t if c.isdigit())

            features.append([
                float(fee_cues) * 2.0,
                float(pay_advance) * 2.0,
                float(refundable) * 1.5,
                float(kyc_harvest) * 1.8,
                float(urgency) * 1.0,
                float(off_platform) * 1.2,
                float(unreal_promise) * 1.5,
                float(investment_task) * 1.8,
                float(legit_cues) * 2.0,
                min(caps_ratio * 3.0, 3.0),
                min(exclamation_count / 3.0, 2.0),
                min(currency_count / 3.0, 2.0),
                min(digit_count / 20.0, 2.0),
            ])

        return np.array(features)
