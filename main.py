from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os

from core.database import Base, engine
from core.auth import verificar_contrasena, SESSION_KEY, esta_autenticado

from modules.turnos import models as turnos_models
from modules.stock import models as stock_models

from modules.turnos.routes import router as turnos_router
from modules.stock.routes import router as stock_router
from core.auth_middleware import AuthMiddleware
app = FastAPI()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "clave-local-desarrollo")
)

app.add_middleware(AuthMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

app.include_router(turnos_router)
app.include_router(stock_router)


# ------------------------
# MIDDLEWARE DE AUTENTICACION
# Intercepta TODAS las requests antes de llegar a las rutas.
# Si la URL no es /login y no está autenticado, redirige al login.
# ------------------------

#@app.middleware("http")
#async def verificar_sesion(request: Request, call_next):
#    rutas_publicas = ["/login", "/static"]
#   es_publica = any(request.url.path.startswith(r) for r in rutas_publicas)
#
#   if not es_publica and not esta_autenticado(request):
#        return RedirectResponse("/login", status_code=303)
#
#    return await call_next(request)


# ------------------------
# LOGIN / LOGOUT
# ------------------------

@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": False
    })


@app.post("/login")
def login(request: Request, contrasena: str = Form(...)):
    if verificar_contrasena(contrasena):
        request.session[SESSION_KEY] = True
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": True
    })


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)