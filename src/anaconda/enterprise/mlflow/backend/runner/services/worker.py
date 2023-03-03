import shlex
import shutil
import subprocess

from ..contracts.requests.execute import ExecuteRequest


class WorkerService:
    """ """

    @staticmethod
    def _process_launch_wait(cwd: str, shell_out_cmd: str) -> None:
        """
        Internal function for wrapping process launches [and waiting].

        Parameters
        ----------
        shell_out_cmd: str
            The command to be executed.
        """

        args = shlex.split(shell_out_cmd)

        with subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE) as process:
            for line in iter(process.stdout.readline, b""):
                print(line)

    @staticmethod
    def execute(project_path: str, request: ExecuteRequest):
        print("Processing mlflow step")
        WorkerService._process_launch_wait(cwd=project_path, shell_out_cmd=request.command)
        print("Complete")

        # After completion, remove cache
        # print("Removing worker cache")
        # shutil.rmtree(path=project_path)
