from typing import Dict

from anaconda.enterprise.server.contracts import BaseModel


class ExecuteRequest(BaseModel):
    # TODO: base64 encoded archive (as per security discussion for multi-user deployment)
    project_id: str
    command: str
    variables: Dict[str, str]
