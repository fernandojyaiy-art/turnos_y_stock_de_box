from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.auth import esta_autenticado


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        rutas_publicas = ["/login", "/static"]

        es_publica = any(
            request.url.path.startswith(r)
            for r in rutas_publicas
        )

        if not es_publica and not esta_autenticado(request):
            return RedirectResponse("/login", status_code=303)

        return await call_next(request)