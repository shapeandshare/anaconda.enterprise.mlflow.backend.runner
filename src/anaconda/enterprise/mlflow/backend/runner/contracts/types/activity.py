from enum import Enum


class ActivityType(str, Enum):
    """Type of activity to occur"""

    SERVER = "server"
    WORKER = "worker"
