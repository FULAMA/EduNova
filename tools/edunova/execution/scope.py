from enum import Enum


class ExecutionScope(str, Enum):
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"
    PROJECT = "PROJECT"
    TEST_SUITE = "TEST_SUITE"
    GIT = "GIT"
    DATABASE = "DATABASE"
    EXTERNAL = "EXTERNAL"
    SYSTEM = "SYSTEM"
