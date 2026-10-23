from enum import Enum


class ExecutionAction(str, Enum):
    READ = "READ"
    SCAN = "SCAN"
    ANALYZE = "ANALYZE"
    PLAN = "PLAN"
    TEST = "TEST"
    QUALITY = "QUALITY"
    SECURITY = "SECURITY"
    GENERATE = "GENERATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    INSTALL = "INSTALL"
    MIGRATE = "MIGRATE"
    GIT_COMMIT = "GIT_COMMIT"
    GIT_PUSH = "GIT_PUSH"
    SHELL = "SHELL"
