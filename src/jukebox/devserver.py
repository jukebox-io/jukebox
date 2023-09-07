import logging
import multiprocessing
import os
import pathlib
import sys
import time
import typing
import uvicorn
import watchfiles

from jukebox.logging import configure_logging
from jukebox.config import ROOT_DIR

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


def start_server() -> None:
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
            start_worker(server.run, options, [socket])

        # wait for file changes
        try:
            change_list: set[FileChange] = next(file_watcher)
            logger.debug(
                "Watchfiles detected changes in %s. Reloading ...", stringify_changes(change_list)
            )

        except (StopIteration, KeyboardInterrupt):
            break

    # conclude
    time.sleep(1)
    logger.info("Server stopped !!!")


# Starts a new worker process and returns its instance


def start_worker(target: typing.Callable, options: uvicorn.Config, *args, **kwargs) -> ctx.Process:
    try:
        in_stream = sys.stdin.fileno()
    except OSError:
        in_stream = None

    def _child(
        target: typing.Callable,
        options: uvicorn.Config,
        addt_args: list,
        addt_kwargs: dict,
        in_stream: int = None,
    ) -> None:
        if in_stream is not None:
            sys.stdin = os.fdopen(in_stream)

        # configure logging
        configure_logging()
        options.configure_logging()  # uvicorn logging

        # execute
        target(*addt_args, **addt_kwargs)

    # build process
    p = ctx.Process(
        target=_child,
        kwargs={
            "target": target,
            "options": options,
            "addt_args": args,
            "addt_kwargs": kwargs,
            "in_stream": in_stream,
        },
    )

    # start process
    p.start()
    active_workers.append(p)

    return p


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
