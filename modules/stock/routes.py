from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from core.database import get_db
from . import services
from modules.turnos import services as turnos_services

router = APIRouter(prefix="/stock")
templates = Jinja2Templates(directory="templates")


# ------------------------
# PRODUCTOS — lista y alta
# ------------------------

@router.get("/productos")
def productos_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("productos.html", {
        "request": request,
        "productos": services.listar_productos(db)
    })


@router.post("/productos/crear")
def crear_producto(
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db)
):
    services.crear_producto(db, nombre, precio, stock)
    return RedirectResponse("/stock/productos", status_code=303)


@router.get("/productos/editar/{producto_id}")
def editar_producto_form(producto_id: int, request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("editar_producto.html", {
        "request": request,
        "producto": services.obtener_producto(db, producto_id)
    })


@router.post("/productos/editar/{producto_id}")
def editar_producto(
    producto_id: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db)
):
    services.editar_producto(db, producto_id, nombre, precio, stock)
    return RedirectResponse("/stock/productos", status_code=303)


@router.get("/productos/eliminar/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    services.eliminar_producto(db, producto_id)
    return RedirectResponse("/stock/productos", status_code=303)


# ------------------------
# REGISTRAR VENTA
# ------------------------

@router.get("/venta/{cliente_id}")
def venta_form(cliente_id: int, request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("venta.html", {
        "request": request,
        "cliente": turnos_services.obtener_cliente(db, cliente_id),
        "productos": services.listar_productos(db),
        "error": None
    })


@router.post("/venta/{cliente_id}")
def registrar_venta(
    cliente_id: int,
    request: Request,
    producto_id: int = Form(...),
    cantidad: int = Form(...),
    db: Session = Depends(get_db)
):
    venta, error = services.registrar_venta(db, cliente_id, producto_id, cantidad)

    if error:
        return templates.TemplateResponse("venta.html", {
            "request": request,
            "cliente": turnos_services.obtener_cliente(db, cliente_id),
            "productos": services.listar_productos(db),
            "error": error
        })

    return RedirectResponse(f"/clientes/{cliente_id}", status_code=303)