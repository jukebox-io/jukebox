from fastapi import FastAPI

from jukebox.logger import configure_logging

# we configure the logging level and format
configure_logging()

app = FastAPI()


@app.get("/")
async def hello_world() -> str:
    return "Hello, world!"
