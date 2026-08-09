"""
JobShield AI — ML Feature Extractor Link
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.feature_extractor import ScamDomainFeatureExtractor

__all__ = ["ScamDomainFeatureExtractor"]
