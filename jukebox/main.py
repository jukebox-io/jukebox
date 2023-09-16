from fastapi import FastAPI

from jukebox.logger import setup_loggers

# we configure the logging level and format
setup_loggers()

app = FastAPI()


@app.get("/")
async def hello_world() -> str:
    return "Hello, world!"
