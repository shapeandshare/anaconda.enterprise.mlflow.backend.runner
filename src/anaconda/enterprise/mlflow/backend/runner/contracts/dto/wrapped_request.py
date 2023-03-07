""" Wrapped Request Definition """

from typing import Dict, Optional

from pydantic import Field

from anaconda.enterprise.server.contracts import BaseModel

from ...contracts.types.request_verb import RequestVerb
from .request_status_codes import RequestStatusCodes


class WrappedRequest(BaseModel):
    """
    Wrapped Request DTO

    Attributes
    ----------
    verb: RequestVerb
        The verb of the REST API request.
    statuses: RequestStatusCodes
        The status code assignments for response handling.
    url: str
        The URL for the request.
    json_request: Optional[Dict]
        Either form data or body (based on type - see requests documentation)
    data: Optional[Dict]
        Either form data or body (based on type - see requests documentation)
    files: Optional[Dict]:
        An optional dictionary of `project_file` keys to file bytes.
    params: Optional[Dict[str, str]]
        Query parameters
    """

    verb: RequestVerb
    statuses: RequestStatusCodes
    url: str

    # Declared this way due to a conflict within Pydantic.
    json_request: Optional[dict] = Field(alias="json", default=None)

    data: Optional[dict] = None
    files: Optional[dict] = None
    params: Optional[Dict[str, str]] = None
