from typing import Any, Optional

from anaconda.enterprise.server.contracts import BaseModel

from ..contracts.dto.command_options import CommandOptions
from ..contracts.requests.execute import ExecuteRequest
from ..contracts.responses.execute import ExecuteResponse
from ..sdk.commands.execute import ExecuteCommand


class RunnerClient(BaseModel):
    execute_command: Optional[ExecuteCommand]

    def __init__(self, **data: Any):
        super().__init__(**data)

        default_command_options: CommandOptions = CommandOptions(sleep_time=1.0, retry_count=10, timeout=5)

        if not self.execute_command:
            self.execute_command = ExecuteCommand(options=default_command_options)

    def execute(self, project_id: str, command: str, variables: Dict[str, str]) -> ExecuteResponse:
        request: ExecuteRequest = ExecuteRequest.parse_obj(
            {"project_id": project_id, "command": command, "variables": variables}
        )
        return self.execute_command.execute(request=request)
