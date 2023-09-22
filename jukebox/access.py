import urllib

from fastapi import Request

from jukebox.logging import Logger

REQ_LOG_FMT: str = '[BEGIN] {address} - "{method} {path} HTTP/{version}"'
RES_LOG_FMT: str = '[END  ] {address} - "{method} {path} HTTP/{version}" {status}'


def log_request(request: Request) -> None:
    # Log a request
    Logger.info(
        REQ_LOG_FMT,
        address=client_address(request),
        method=request.method,
        path=path_with_query(request),
        version=http_version(request),
    )


def log_response(request: Request, status_code: int, exc_info=None) -> None:
    # Log a response
    Logger.info(
        RES_LOG_FMT,
        address=client_address(request),
        method=request.method,
        path=path_with_query(request),
        version=http_version(request),
        status=status_code,
        exception=exc_info,
    )


def client_address(request: Request) -> str:
    # Extract the client address from the request object
    client = request.get("client")
    if not client:
        return ":-1"
    return "%s:%d" % client


def path_with_query(request: Request) -> str:
    # Extract the path with query string from the request object
    path: str = urllib.parse.quote(request.get("path"))
    query_string: bytes | None = request.get("query_string")

    if query_string:
        path += "?" + query_string.decode("ascii")

    return path


def http_version(request: Request) -> str:
    # Extract the http version from the request object
    version = request.get("http_version")
    if not version:
        return "-1"
    return version
