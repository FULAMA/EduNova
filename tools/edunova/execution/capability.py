from enum import Enum


class ExecutionCapability(str, Enum):
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    PROCESS_EXECUTE = "process.execute"
    GIT_READ = "git.read"
    GIT_WRITE = "git.write"
    NETWORK_ACCESS = "network.access"
    DATABASE_READ = "database.read"
    DATABASE_WRITE = "database.write"
