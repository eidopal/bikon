from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def success_response(data=None, msg="Success", code=200):
    """统一成功响应"""
    return {"code": code, "msg": msg, "data": data}


def error_response(msg="Error", code=400, detail=None):
    """统一错误响应"""
    return {"code": code, "msg": msg, "detail": detail}


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数验证错误"""
    return JSONResponse(
        status_code=422,
        content=error_response(
            msg="Validation error",
            code=422,
            detail=exc.errors(),
        ),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理 HTTP 异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            msg=exc.detail if isinstance(exc.detail, str) else "HTTP error",
            code=exc.status_code,
            detail=exc.detail,
        ),
    )


async def global_exception_handler(request: Request, exc: Exception):
    """处理未捕获的全局异常"""
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content=error_response(
            msg="Internal server error",
            code=500,
            detail=str(exc),
        ),
    )
