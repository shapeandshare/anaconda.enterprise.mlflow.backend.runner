""" Command Options Definition """

from anaconda.enterprise.server.contracts import BaseModel


class CommandOptions(BaseModel):
    """
    Command Options DTO

    Attributes
    ----------
    sleep_time: float
        Sleep time in seconds.
    retry_count: int
        Maximum number of retries.
    timeout: float
        Time out in seconds.
    """

    sleep_time: float
    retry_count: int
    timeout: float
