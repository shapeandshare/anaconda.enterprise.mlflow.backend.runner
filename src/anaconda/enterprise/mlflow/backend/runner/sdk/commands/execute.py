from starlette import status

from anaconda.enterprise.server.common.sdk import demand_env_var

from ..contracts.dto.request_status_codes import RequestStatusCodes
from ..contracts.dto.wrapped_request import WrappedRequest
from ..contracts.requests.execute import ExecuteRequest
from ..contracts.responses.execute import ExecuteResponse
from ..contracts.types.request_verb import RequestVerb
from .abstract_command import AbstractCommand


class ExecuteCommand(AbstractCommand):
    """"""

    def execute(self, request: ExecuteRequest) -> ExecuteResponse:
        request: WrappedRequest = WrappedRequest(
            verb=RequestVerb.POST,
            url=f"https://{demand_env_var(name='RUNNER_HOSTNAME')}/api/v1/execute",
            json=request.dict(by_alias=False),
            statuses=RequestStatusCodes(
                allow=[status.HTTP_201_CREATED], reauth=[status.HTTP_401_UNAUTHORIZED], retry=[]
            ),
        )
        response: dict = self.wrapped_request(request=request, options=self.options)
        return ExecuteResponse.parse_obj(response)
