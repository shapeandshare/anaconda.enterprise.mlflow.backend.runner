import tarfile
from pathlib import Path

from ..contracts.errors.tar import TarServiceError


class TarService:
    @staticmethod
    def expand(filename: Path, destination: Path) -> None:
        if not tarfile.is_tarfile(name=filename.as_posix()):
            message: str = f"{filename.as_posix()} was not a tar archive"
            raise TarServiceError(message)

        with tarfile.open(name=filename.as_posix()) as tar:
            tar.extractall(path=destination.as_posix())
