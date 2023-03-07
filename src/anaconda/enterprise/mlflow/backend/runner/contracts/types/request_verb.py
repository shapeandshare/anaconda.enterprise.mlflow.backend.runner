""" Request Verb Definition """

from enum import Enum


class RequestVerb(str, Enum):
    """Defines the types of requests supported."""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
