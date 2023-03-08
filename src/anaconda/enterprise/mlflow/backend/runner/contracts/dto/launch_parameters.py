""" API Launch Parameters Definition """

from anaconda.enterprise.server.contracts import BaseModel

from ..types.activity import ActivityType


# pylint: disable=too-few-public-methods
class LaunchParameters(BaseModel):
    """
    Runner API Launch Parameters (DTO)

    port: str
        The port to start the server listening on.  This is meant to be automatically set by AE5.
    address: str
        The address to start the server listening on.  This is meant to be automatically set by AE5.
    """

    port: int = 8086
    address: str = "0.0.0.0"
    activity: ActivityType
