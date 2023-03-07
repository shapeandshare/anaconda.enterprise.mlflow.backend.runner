import json
import shlex
import subprocess
from typing import Dict

from anaconda.enterprise.server.common.sdk import demand_env_var
from anaconda.enterprise.server.contracts import BaseModel

from .sdk.contracts.dto.launch_parameters import LaunchParameters
from .sdk.contracts.requests.execute import ExecuteRequest
from .sdk.contracts.types.activity import ActivityType
from .services.worker import WorkerService


# pylint: disable=too-few-public-methods
class AEMLFlowBackendRunnerController(BaseModel):
    """
    Responsible for the invocation of the mlflow process.
    """

    @staticmethod
    def _process_launch_wait(shell_out_cmd: str) -> None:
        """
        Internal function for wrapping process launches [and waiting].

        Parameters
        ----------
        shell_out_cmd: str
            The command to be executed.
        """

        args = shlex.split(shell_out_cmd)

        with subprocess.Popen(args, stdout=subprocess.PIPE) as process:
            for line in iter(process.stdout.readline, b""):
                print(line)

    def execute(self, params: LaunchParameters) -> None:
        """
        This function is responsible for mapping AE5 arguments to mlflow launch arguments and then
        executing the service.

        Parameters
        ----------
        params: LaunchParameters
            Parameters needed for Runner API Configuration.
        """

        if params.activity == ActivityType.SERVER:
            AEMLFlowBackendRunnerController.launch_server(params=params)
        elif params.activity == ActivityType.WORKER:
            AEMLFlowBackendRunnerController.launch_worker()
        else:
            message = f"launch type {params.activity} is not supported"
            raise ValueError(message)

    @staticmethod
    def launch_server(params: LaunchParameters) -> None:
        cmd: str = f"uvicorn src.anaconda.enterprise.mlflow.backend.runner.api.main:app --host {params.address} --port {params.port}"
        print(cmd)
        AEMLFlowBackendRunnerController._process_launch_wait(shell_out_cmd=cmd)

    @staticmethod
    def launch_worker():
        manifest_path: str = demand_env_var(name="MANIFEST_FILE_PATH")
        print(f"Launching worker with manifest: {manifest_path}")
        with open(file=manifest_path, mode="r", encoding="utf-8") as file:
            manifest_data: Dict = json.load(file)
            print(manifest_data)
            project_path: str = manifest_data["project_path"]
            request: ExecuteRequest = ExecuteRequest.parse_obj(manifest_data["request"])
            WorkerService.execute(project_path=project_path, request=request)
