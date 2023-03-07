""" Abstract Command Definition """
import time
from abc import abstractmethod
from typing import Any, Optional

import requests
from requests import Response, Session

from anaconda.enterprise.server.common.sdk import demand_env_var
from anaconda.enterprise.server.contracts import BaseModel

from ...contracts.dto.command_options import CommandOptions
from ...contracts.dto.wrapped_request import WrappedRequest
from ...contracts.errors.exceeded_retry_count_error import ExceededRetryCountError
from ...contracts.errors.request_failure_error import RequestFailureError
from ...contracts.types.request_verb import RequestVerb


class AbstractCommand(BaseModel):
    """
    Abstract Command

    Attributes
    ----------
    options: CommandOptions
        The configuration options for the command.
    """

    options: CommandOptions
    session: Optional[Session] = None

    @abstractmethod
    def execute(self, *args, **kwargs) -> Optional[Any]:
        """
        Command entry point
        This is to be implemented when sub-classed.
        """

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.session: Session = requests.Session()
        self.session.verify = False

    def _build_requests_params(self, request: WrappedRequest, options: CommandOptions) -> dict:
        """
        Builds the `requests` call parameters.

        Parameters
        ----------
        request: WrappedRequest
            The request to make.

        Returns
        -------
        params: dict
            A dictionary suitable for splatting into the `requests` call.
        """

        params: dict = {
            "url": request.url,
            "timeout": options.timeout,
        }
        if request.verb == RequestVerb.POST:
            if request.json_request is not None:
                params["json"] = request.json_request
            if request.data is not None:
                params["data"] = request.data
        if request.params is not None:
            params["params"] = request.params
        if request.files is not None:
            params["files"] = request.files
        return params

    def _api_caller(self, request: WrappedRequest, depth: int, options: CommandOptions) -> Optional[dict]:
        """
        Wrapper for calls with `requests` to external APIs.

        Parameters
        ----------
        request: WrappedRequest
            Request to make.
        depth: int
            Call depth of the recursive call (retry)

        Returns
        -------
        response: dict
            A dictionary of the response.
        """

        if depth < 1:
            raise ExceededRetryCountError(json.dumps({"request": request.dict(), "depth": depth}))
        depth -= 1

        params: dict = self._build_requests_params(request=request, options=options)
        # pylint: disable=broad-except
        try:
            if request.verb == RequestVerb.GET:
                response: Response = self.session.get(**params)
            elif request.verb == RequestVerb.POST:
                response: Response = self.session.post(**params)
            elif request.verb == RequestVerb.DELETE:
                response: Response = self.session.delete(**params)
            else:
                raise Exception("Unknown Verb")
        except requests.exceptions.ConnectionError as error:
            logging.debug("Connection Error (%s) - Retrying.. %i", str(error), depth)
            time.sleep(options.sleep_time)
            return self._api_caller(request=request, depth=depth, options=options)
        except Exception as error:
            logging.debug("Exception needed to cover: %s", str(error))
            time.sleep(options.sleep_time)
            return self._api_caller(request=request, depth=depth, options=options)

        if response.status_code in request.statuses.allow:
            if response.content == b"":
                return None
            return response.json()

        if response.status_code in request.statuses.retry:
            time.sleep(options.sleep_time)
            return self._api_caller(request=request, depth=depth, options=options)

        if response.status_code in request.statuses.reauth:
            self.authorize()
            return self._api_caller(request=request, depth=depth, options=options)

        # print(response)
        # print(response.status_code)
        raise RequestFailureError(status_code=response.status_code, request=request.dict(), depth=depth)

    def authorize(self) -> None:
        self.session.headers["Authorization"] = f"Bearer {demand_env_var(name='RUNNER_AUTH_TOKEN')}"

    def wrapped_request(self, request: WrappedRequest, options: CommandOptions) -> Optional[dict]:
        """
        High level request method.  Entry point for consumption.


        Parameters
        ----------
        request: WrappedRequest
            The request to make.
        options: CommandOptions
            Command Options controlling execution behavior.

        Returns
        -------
        response: dict
            The response as a dictionary.
        """

        return self._api_caller(request=request, depth=options.retry_count, options=options)
