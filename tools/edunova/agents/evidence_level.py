from enum import Enum


class EvidenceLevel(str, Enum):
    OBSERVED = "observed"
    UNKNOWN = "unknown"
    HYPOTHESIS = "hypothesis"
    RECOMMENDATION = "recommendation"
