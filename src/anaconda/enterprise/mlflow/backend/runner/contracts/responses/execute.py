from typing import Optional

from anaconda.enterprise.server.contracts import BaseModel


class ExecuteResponse(BaseModel):
    request_id: str
    job_id: Optional[str] = None
