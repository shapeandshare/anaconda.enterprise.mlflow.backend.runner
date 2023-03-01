import shlex
import subprocess

from anaconda.enterprise.server.contracts import BaseModel

from .contracts.dto.launch_parameters import LaunchParameters
from .contracts.types.activity import ActivityType


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
            self.launch_worker()
        else:
            message = f"launch type {params.activity} is not supported"
            raise ValueError(message)

    @staticmethod
    def launch_server(params: LaunchParameters) -> None:
        cmd: str = f"uvicorn src.anaconda.enterprise.mlflow.backend.runner.api.main:app --host {params.address} --port {params.port}"
        print(cmd)
        AEMLFlowBackendRunnerController._process_launch_wait(shell_out_cmd=cmd)

    def launch_worker(self):
        pass
