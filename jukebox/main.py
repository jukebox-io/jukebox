import os
import typing

import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import PlainTextResponse

from jukebox.access import log_request, log_response
from jukebox.logging import Logger

app = FastAPI()


@app.on_event("startup")
async def initialize() -> None:
    # Log initialization
    Logger.info("Booting worker with pid: {}", os.getpid())


@app.on_event("shutdown")
async def finalize() -> None:
    # Log termination
    Logger.info("Stopping worker with pid: {}", os.getpid())


@app.middleware("http")
async def log_http_request(request: Request, call_next: typing.Callable[..., typing.Awaitable[Response]]) -> Response:
    # Log the request and response
    log_request(request)
    response: Response = await call_next(request)
    log_response(request, response.status_code)

    return response


@app.exception_handler(Exception)
async def server_crash_handler(request: Request, exc: Exception) -> Response:
    # Log error response
    log_response(request, status.HTTP_500_INTERNAL_SERVER_ERROR, exc_info=exc)

    return PlainTextResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="Internal Server Error",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)
