# import logging
import json
import uuid
from pathlib import Path
from typing import Dict, Optional

from ae5_tools.api import AEException, AEUserSession
from starlette import status
from starlette.exceptions import HTTPException

from anaconda.enterprise.server.common.sdk import EnvironmentVariableNotFoundError, demand_env_var
from anaconda.enterprise.server.contracts import BaseModel, JobCreateResponse

from src.anaconda.enterprise.mlflow.backend.runner.contracts.errors.tar_error import TarServiceError
from ...sdk.contracts.requests.execute import ExecuteRequest
from ...sdk.contracts.responses.execute import ExecuteResponse
from ...services.tar import TarService

# logger = logging.getLogger(__name__)
# logger.setLevel(level=logging.DEBUG)


class ExecuteCommand(BaseModel):
    ae_session: AEUserSession
    tar_service: TarService

    def download_project(self, request: ExecuteRequest, request_id: str, request_cache_path: Path) -> Path:
        archive_filename: str = f"{request.project_id}.tar.gz"
        request_cache_path.mkdir(parents=True, exist_ok=True)
        file_path: str = (request_cache_path / archive_filename).as_posix()

        try:
            self.ae_session.project_download(ident=request.project_id, filename=file_path)
        except AEException as error:
            print(error)
            message: Dict = {"message": "Unable to locate project to execute", "request_id": request_id}
            try:
                request_cache_path.rmdir()
            except Exception as inner_error:
                message["inner_error"] = str(inner_error)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message) from error

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from error

        return Path(file_path)

    def get_cache_path(self, request_id: str) -> Path:
        return Path(".") / demand_env_var(name="RUNNER_PERSISTENT_STORAGE") / request_id

    def execute(self, request: ExecuteRequest) -> ExecuteResponse:
        # logger.debug(request.json())
        print(request.json())

        self.ae_session._connect(password=self.ae_session)

        # 1. Download the project by id and revision (store in unique location in persistent storage)
        # 2. Expand the archive
        # 3. Create execution manifest for request and place into project on file system.
        # 4. invoke job entry point with needed details

        request_id: str = str(uuid.uuid4())
        request_cache_path: Path = self.get_cache_path(request_id=request_id)

        print(f"Request ID: {request_id}")
        print(f"Cache path for request: {request_cache_path.as_posix()}")

        # 1. Download the project
        file_path: Path = self.download_project(
            request=request, request_id=request_id, request_cache_path=request_cache_path
        )

        # 2. Expand the archive
        try:
            self.tar_service.expand(filename=file_path, destination=request_cache_path)
        except TarServiceError as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

        # Determine the inner path
        inner_path: Optional[Path] = None
        for item in request_cache_path.glob("*"):
            if Path(item).is_dir():
                inner_path = item
                break
        print(inner_path)

        # 3. Create execution manifest for request and place into project on file system.
        manifest: Dict = {"request_id": request_id, "project_path": inner_path.as_posix(), "request": request.dict()}
        with open(file=(request_cache_path / "manifest.json").as_posix(), mode="w", encoding="utf-8") as file:
            file.write(json.dumps(manifest))

        # Setup job variables
        # TODO: black listed variable list (mlflow, or ae configs)?
        job_env_variables: Dict[str, str] = {
            **request.variables,
            "MANIFEST_FILE_PATH": (request_cache_path / "manifest.json").as_posix(),
        }

        # 4. Invoke job entry point with needed details
        job_create_params: Dict = {
            "name": request_id,
            "ident": ExecuteCommand.get_project_id(),
            "command": "Worker",
            "variables": job_env_variables,
            "run": True,
        }
        try:
            print(job_create_params)
            response_dict: dict = self.ae_session.job_create(**job_create_params)
            response: JobCreateResponse = JobCreateResponse.parse_obj(response_dict)
            print(response.dict())
        except Exception as error:
            print(error)
            message: Dict = {"message": "Unable to start job", "request_id": request_id, "params": job_create_params}

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from error

        return ExecuteResponse(request_id=request_id, job_id=response.id)

    @staticmethod
    def get_project_id() -> str:
        try:
            # Sample:
            # APP_SOURCE=http://anaconda-enterprise-ap-storage/projects/f2dff223d2cc40a2b7f80a1318aceb5d/archive/0.0.1
            return f"a0-{demand_env_var(name='APP_SOURCE').split(sep='/')[4]}"

        except EnvironmentVariableNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to determine app source for project. Not running within Anaconda Enterprise?",
            ) from error
