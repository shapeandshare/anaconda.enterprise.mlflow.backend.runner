from anaconda.enterprise.server.contracts import BaseModel


class ExecuteRequest(BaseModel):
    project_id: str
    command: str
