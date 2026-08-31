from fastapi import FastAPI
from starlette.exceptions import HTTPException
from fastapi.requests import Request
from starlette.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})


def init_handler_errors(app: FastAPI):
    #  注意必须是：starlette.exceptions 中的 HTTPException
    app.add_exception_handler(HTTPException, handler=http_exception_handler)
