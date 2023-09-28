import os
import pathlib

ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parents[1]
RESOURCE_DIR: pathlib.Path = ROOT_DIR / "resources"

ID_TITLE: str = "JukeBox API Server"
ID_VERSION: str = "0.3.0"

WSGI_APPLICATION_URL: str = "jukebox.main:app"

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan> <bold>[{process.id}] {thread.name}</bold> - {message}"
)
