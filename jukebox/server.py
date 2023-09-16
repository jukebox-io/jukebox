import logging
import multiprocessing
import os
import pathlib
import sys
import time
import typing
import uvicorn
import watchfiles

from jukebox.logger import setup_loggers
from jukebox.globals import ROOT_DIR

logger = logging.getLogger(__name__)

RUN_CONFIG: dict[str, typing.Any] = {
    "app": "jukebox.main:app",
    "host": "localhost",
    "port": 8000,
    "workers": 4,
    "log_config": None,
}

# Get the process context
multiprocessing.allow_connection_pickling()
ctx = multiprocessing.get_context("spawn")

# List of currently running processes
active_workers: list[ctx.Process] = []


# Starts the dev server and wait for file changes
def serve_develop() -> None:
    # configure logging
    setup_loggers()

    logger.info(
        "Starting development server at http://%s:%d/", RUN_CONFIG["host"], RUN_CONFIG["port"]
    )
    logger.info("Quit the server with CONTROL-C.")

    options = uvicorn.Config(**RUN_CONFIG)
    socket = options.bind_socket()

    server = uvicorn.Server(options)

    file_watcher = watchfiles.watch(ROOT_DIR)

    while True:
        # stop all active workers
        while active_workers:
            worker = active_workers.pop()
            worker.terminate()
            worker.join()

        # initialize workers
        for _ in range(options.workers):
            start_worker(server.run, [socket], server_config=options)

        # wait for file changes
        try:
            change_list: set[FileChange] = next(file_watcher)
            logger.info(
                "Watchfiles detected changes in %s. Reloading ...", stringify_changes(change_list)
            )

        except (StopIteration, KeyboardInterrupt):
            break

    # conclude
    while active_workers:
        worker = active_workers.pop()
        worker.join()

    time.sleep(1)
    logger.info("Server stopped !!!")


# Starts a new worker process and returns its instance
def start_worker(
    target: typing.Callable, *pargs, server_config: uvicorn.Config = None, **pkwargs
) -> ctx.Process:
    try:
        stdin_fno = sys.stdin.fileno()
    except OSError:
        stdin_fno = None

    # build process
    p = ctx.Process(
        target=exec_target,
        kwargs={
            "target": target,
            "pargs": pargs,
            "pkwargs": pkwargs,
            "stdin_fno": stdin_fno,
            "server_config": server_config,
        },
    )

    # start process
    p.start()
    active_workers.append(p)

    return p


def exec_target(
    target: typing.Callable[..., None] = None,
    pargs: list = [],
    pkwargs: dict = {},
    stdin_fno: int = None,
    server_config: uvicorn.Config = None,
) -> None:
    # re-open input stream
    if stdin_fno is not None:
        sys.stdin = os.fdopen(stdin_fno)

    # re-configure logging
    setup_loggers()

    if server_config:
        server_config.configure_logging()  # uvicorn logging

    # execute target
    if target:
        target(*pargs, **pkwargs)


"""
A tuple representing a file change, first element is a [`Change`][watchfiles.Change] member, second is the path
of the file or directory that changed.
"""
FileChange = tuple[watchfiles.Change, str]


def stringify_changes(changes: set[FileChange]) -> str:
    affected_paths: list[str] = []

    for c in changes:
        path = pathlib.Path(c[1])
        try:
            path = path.relative_to(ROOT_DIR)
        except ValueError:
            ...
        affected_paths.append(str(path))

    return ", ".join(affected_paths)


def entrypoint() -> None:
    serve_develop()
