from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello_world() -> str:
    return "Hello, world!"
