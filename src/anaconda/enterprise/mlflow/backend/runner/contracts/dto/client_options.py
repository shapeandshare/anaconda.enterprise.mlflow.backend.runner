""" Anaconda Enterprise Client Options Definition """

from typing import Optional

from anaconda.enterprise.server.contracts import BaseModel


class ClientOptions(BaseModel):
    """
    Anaconda Enterprise Client Options Definition DTO

    Attributes
    ----------
    hostname: Optional[str]
        The hostname of the Anaconda Enterprise Server.
    username: Optional[str]
        The user's name.
    password: Optional[str]
        The user's password.
    """

    hostname: Optional[str] = None

    username: Optional[str] = None
    password: Optional[str] = None
