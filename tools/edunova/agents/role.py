from enum import Enum


class AgentRole(str, Enum):
    INSPECTOR = "INSPECTOR"
    ARCHITECT = "ARCHITECT"
    BUILDER = "BUILDER"
    REVIEWER = "REVIEWER"
    QA = "QA"
    SECURITY = "SECURITY"
    DOCUMENTATION = "DOCUMENTATION"
