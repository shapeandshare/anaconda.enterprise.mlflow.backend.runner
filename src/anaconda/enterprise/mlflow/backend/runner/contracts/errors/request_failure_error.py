""" Request Failure Error Definition """


class RequestFailureError(Exception):
    """Request Failure Error"""

    status_code: int
    request: dict
    depth: int

    def __init__(self, status_code: int, request: dict, depth: int):
        super().__init__()

        self.status_code = status_code
        self.request = request
        self.depth = depth
