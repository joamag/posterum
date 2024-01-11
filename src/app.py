import uvicorn

from os import environ
from time import time
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from posterum import SMTPVerifier, PosterumError

NAME = "posterum"
VERSION = "0.1.1"
DESCRIPTION = "Simple e-mail address SMTP verification service"

app = FastAPI(
    title=NAME,
    version=VERSION,
    description=DESCRIPTION,
)


@app.get("/")
@app.get("/index")
async def index():
    return JSONResponse(dict(name=NAME, version=VERSION, timestamp=time()))


@app.get("/ping")
@app.get("/api/v1/ping")
async def ping():
    return JSONResponse(dict(pong=True, timestamp=time()))


@app.get("/v1/addresses/validate")
@app.get("/api/v1/addresses/validate")
async def address_validate(
    address: str | None = None,
    email: str | None = None,
    cache: bool | None = None,
    key: str | None = None,
):
    secret_key = environ.get("SECRET_KEY", None)

    address = address or email

    if secret_key and not key == secret_key:
        raise RuntimeError("Invalid key")

    if not address:
        raise RuntimeError("Missing email address")

    # runs the effective SMTP validation test for the address
    # and obtains the result of the validation, to be used in
    # the sending of the response
    result = await SMTPVerifier.validate_email(address, cache=cache)

    return JSONResponse(dict(address=address, **(result.to_dict() if result else {})))


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    code = 500
    payload = None
    if isinstance(exc, PosterumError):
        exc = cast(PosterumError, exc)
        code = exc.code
        payload = exc.payload
    content: dict[str, Any] = dict(
        message=str(exc), name=exc.__class__.__name__, code=code
    )
    if payload:
        content["payload"] = payload
    return JSONResponse(status_code=code, content=content)


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=environ.get("HOST", "0.0.0.0"),
        port=int(environ.get("PORT", "8080")),
        reload=True,
    )
