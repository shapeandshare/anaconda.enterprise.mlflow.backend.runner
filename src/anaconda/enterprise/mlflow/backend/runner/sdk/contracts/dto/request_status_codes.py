""" Request Status Codes Definition """

from typing import List

from anaconda.enterprise.server.contracts import BaseModel


class RequestStatusCodes(BaseModel):
    """
    Request Status Codes DTO

    Attributes
    ----------
    allow: List[int]
        A list of allowed response codes.
    retry: List[int]
        A list of re-try-able response codes.
    reauth: List[int]
        A list of re-authorize-able response codes.
    """

    allow: List[int]
    retry: List[int]
    reauth: List[int]
