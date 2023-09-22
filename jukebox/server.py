import contextlib
import multiprocessing
import os
import pathlib
import sys
import time
import typing

import uvicorn

from jukebox.globals import ROOT_DIR
from jukebox.logging import Logger

RUN_CONFIG: dict[str, typing.Any] = {
    "app": "jukebox.main:app",
    "host": "localhost",
    "port": 8000,
    "workers": 5,
    "log_config": None,
}

# Get the process context
multiprocessing.allow_connection_pickling()
ctx = multiprocessing.get_context("spawn")

# List of currently running processes
active_workers: list[ctx.Process] = []


# Starts the dev server and wait for file changes
def serve_develop() -> None:
    # Import necessary packages
    import watchfiles

    # initialize logging
    Logger.init_logger()

    Logger.info(
        "Starting development server at http://{}:{}/",
        RUN_CONFIG["host"],
        RUN_CONFIG["port"],
    )
    Logger.info("Quit the server with CONTROL-C.")

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
            changes: set[tuple[watchfiles.Change, str]] = next(file_watcher)

            change_list = []
            for change in changes:
                path = change[1]
                with contextlib.suppress(ValueError):
                    path = f"{pathlib.Path(path).relative_to(ROOT_DIR)}"
                change_list.append(path)

            Logger.info("Watchfiles detected changes in {}. Reloading ...", ", ".join(change_list))
        except (StopIteration, KeyboardInterrupt):
            break

    # conclude
    while active_workers:
        worker = active_workers.pop()
        worker.join()

    time.sleep(1)
    Logger.info("Server stopped !!!")


# Starts a new worker process and returns its instance
def start_worker(
    target: typing.Callable,
    *pargs,
    server_config: uvicorn.Config | None = None,
    **pkwargs,
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
    target: typing.Callable[..., None] | None = None,
    pargs: list | None = None,
    pkwargs: dict | None = None,
    stdin_fno: int | None = None,
    server_config: uvicorn.Config = None,
) -> None:
    # re-open input stream
    if pkwargs is None:
        pkwargs = {}
    if pargs is None:
        pargs = []
    if stdin_fno is not None:
        sys.stdin = os.fdopen(stdin_fno)

    # re-initialize logging
    Logger.init_logger()

    if server_config:
        server_config.configure_logging()  # uvicorn logging

    # execute target
    if target:
        target(*pargs, **pkwargs)
