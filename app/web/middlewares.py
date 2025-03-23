import json
import typing

from aiohttp.web_exceptions import HTTPUnprocessableEntity, HTTPException
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )

    except HTTPException as e:
        status_code = e.status
        error_status = HTTP_ERROR_CODES.get(status_code, HTTP_ERROR_CODES[500])

        return error_json_response(
            http_status=status_code,
            status=error_status,
            message=e.reason,
        )

    except Exception as e:
        return error_json_response(
            http_status=403,
            status=HTTP_ERROR_CODES[403],
            message=str(e),
        )

def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
