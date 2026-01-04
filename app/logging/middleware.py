import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .context import request_id_ctx_var

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request_id_ctx_var.set(request_id)

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response