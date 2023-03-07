# import logging

from ae5_tools.api import AEUserSession
from fastapi import FastAPI, status
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from ..contracts.requests.execute import ExecuteRequest
from ..contracts.responses.execute import ExecuteResponse
from ..services.tar import TarService
from .commands.execute import ExecuteCommand
from .utils import get_ae_user_session

# logger = logging.getLogger(__name__)
# logger.setLevel(level=logging.DEBUG)

# Create the FastAPI application
app = FastAPI()

# Create Anaconda Enterprise Session
ae_session: AEUserSession = get_ae_user_session()

#  Apply COR Configuration | https://fastapi.tiangolo.com/tutorial/cors/
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define our commands
tar_service: TarService = TarService()
execute_command: ExecuteCommand = ExecuteCommand(ae_session=ae_session, tar_service=tar_service)


# Define our handlers


@app.get("/health/plain", status_code=status.HTTP_200_OK)
def health_plain() -> bool:
    """
    Get Application Health
    [GET] /health/plain
    Returns
    -------
    [STATUS CODE] 200: OK
        health: bool
            A true/false response of server health.
    """

    return True


@app.post(path="api/v1/execute", response_model=ExecuteResponse, status_code=status.HTTP_201_CREATED)
def execute(request: ExecuteRequest) -> ExecuteResponse:
    """
    Post Execution Request
    [POST] /execute
    Returns
    -------
    [STATUS CODE] 200: CREATED
        response: ExecuteResponse
            The job_id created from the execution.
    """

    # logger.debug("[POST] /execute")
    try:
        return execute_command.execute(request=request)
    except HTTPException as error:
        print(str(error))
        raise error from error
    except Exception as error:
        # Caught all other uncaught errors.
        print(str(error))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
        ) from error
