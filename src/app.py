import uvicorn

from os import environ
from time import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from posterum import SMTPVerifier

app = FastAPI(
    title="Posterum",
    version="0.1.0",
    description="Posterum SMTP validation service.",
)


@app.get("/ping")
@app.get("/api/v1/ping")
async def ping():
    return JSONResponse(content=dict(pong=True, timestamp=time()))


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

    return JSONResponse(
        content=dict(address=address, **(result.to_dict() if result else {}))
    )


if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host=environ.get("HOST", "0.0.0.0"),
        port=int(environ.get("PORT", "8080")),
        reload=True,
    )
