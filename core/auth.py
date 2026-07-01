from fastapi import Request
from fastapi.responses import RedirectResponse
import os

# La contraseña viene de una variable de entorno
# Nunca hardcodeada en el código
CONTRASENA = os.getenv("APP_PASSWORD", "")

SESSION_KEY = "autenticado"


def esta_autenticado(request: Request) -> bool:
    return request.session.get(SESSION_KEY) == True


def login_requerido(request: Request):
    """
    Llama esto al principio de cada ruta protegida.
    Si no está autenticado, devuelve un redirect al login.
    Devuelve None si está OK.
    """
    if not esta_autenticado(request):
        return RedirectResponse("/login", status_code=303)
    return None


def verificar_contrasena(contrasena: str) -> bool:
    return contrasena == CONTRASENA and CONTRASENA != ""