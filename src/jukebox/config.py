import os
import pathlib

ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parents[1]
RESOURCE_DIR: pathlib.Path = ROOT_DIR / "resources"

ID_TITLE: str = "JukeBox API Server"
ID_VERSION: str = "0.3.0"

LOG_FORMAT: str = "%(asctime)s %(name)s [%(process)d] %(threadName)s: %(levelname)s - %(message)s"
LOG_LEVEL: str = os.getenv("LOG_LEVEL") or "INFO"
