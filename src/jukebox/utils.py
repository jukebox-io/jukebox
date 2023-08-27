import pathlib


def root_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parents[1]
