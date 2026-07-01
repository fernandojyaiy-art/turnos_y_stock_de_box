from fastapi import APIRouter, Request, Form, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, time, datetime, timedelta

from core.database import get_db
from . import services

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ------------------------
# AGENDA
# ------------------------

@router.get("/")
def agenda(request: Request, fecha: str = None, db: Session = Depends(get_db)):
    if not fecha:
        ahora = datetime.now()
        if ahora.hour >= 19:
            fecha = (ahora + timedelta(days=1)).date().isoformat()
        else:
            fecha = ahora.date().isoformat()

    profesionales = services.listar_profesionales(db)
    servicios = services.listar_servicios(db)

    if not profesionales or not servicios:
        return templates.TemplateResponse("primer_uso.html", {"request": request})
    grilla = services.armar_grilla(db, fecha)

    return templates.TemplateResponse("agenda.html", {
        "request": request,
        "fecha": fecha,
        "profesionales": profesionales,
        "grilla": grilla,
    })


# ------------------------
# NUEVO TURNO
# ------------------------

@router.get("/nuevo")
def nuevo_turno_form(request: Request, hora: str = None, fecha: str = None, db: Session = Depends(get_db)):
    if not fecha:
        fecha = services.hoy()

    return templates.TemplateResponse("nuevo_turno.html", {
        "request": request,
        "hora": hora,
        "fecha": fecha,
        "profesionales": services.listar_profesionales(db),
        "servicios": services.listar_servicios(db),
        "boxes": services.listar_boxes(db),
        "error": None,
        "turno_pendiente": None,
    })


# ------------------------
# CREAR TURNO
# ------------------------

@router.post("/crear")
def crear_turno(
    request: Request,
    hora: str = Form(...),
    fecha: str = Form(...),
    profesional_id: int = Form(...),
    servicio_id: int = Form(...),
    box_id: int = Form(...),
    confirmado: str = Form("false"),
    monto_seña: float = Form(0),
    forma_pago: str = Form("tarjeta"),
    nombre1: str = Form(...),
    apellido1: str = Form(""),
    telefono1: str = Form(""),
    db: Session = Depends(get_db)
):
    hora_obj = time.fromisoformat(hora + ":00")
    fecha_obj = date.fromisoformat(fecha)

    turno_confirmado = services.box_esta_ocupado(db, box_id, fecha_obj, hora_obj)
    if turno_confirmado:
        return templates.TemplateResponse("nuevo_turno.html", {
            "request": request,
            "hora": hora, "fecha": fecha,
            "profesionales": services.listar_profesionales(db),
            "servicios": services.listar_servicios(db),
            "boxes": services.listar_boxes(db),
            "error": f"El box ya tiene un turno CONFIRMADO a las {hora}.",
            "turno_pendiente": None,
        })

    turno_pendiente = services.box_tiene_pendiente(db, box_id, fecha_obj, hora_obj)
    if turno_pendiente:
        return templates.TemplateResponse("nuevo_turno.html", {
            "request": request,
            "hora": hora, "fecha": fecha,
            "profesionales": services.listar_profesionales(db),
            "servicios": services.listar_servicios(db),
            "boxes": services.listar_boxes(db),
            "error": None,
            "turno_pendiente": turno_pendiente,
            "form_nombre1": nombre1,
            "form_apellido1": apellido1,
            "form_telefono1": telefono1,
            "form_profesional_id": profesional_id,
            "form_servicio_id": servicio_id,
            "form_box_id": box_id,
        })

    cliente1 = services.crear_o_buscar_cliente(db, nombre1, apellido1, telefono1)
    services.crear_turno(db, fecha_obj, hora_obj, cliente1.id, servicio_id, profesional_id, box_id, confirmado == "true", monto_seña, forma_pago)

    return RedirectResponse(f"/?fecha={fecha}", status_code=303)


# ------------------------
# EDITAR TURNO
# ------------------------

@router.get("/turnos/{turno_id}/editar")
def editar_turno_form(turno_id: int, request: Request, db: Session = Depends(get_db)):
    turno = services.obtener_turno(db, turno_id)
    if not turno:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("editar_turno.html", {
        "request": request,
        "turno": turno,
        "profesionales": services.listar_profesionales(db),
        "servicios": services.listar_servicios(db),
        "boxes": services.listar_boxes(db),
        "error": None,
    })


@router.post("/turnos/{turno_id}/editar")
def editar_turno(
    turno_id: int,
    request: Request,
    fecha: str = Form(...),
    hora: str = Form(...),
    profesional_id: int = Form(...),
    servicio_id: int = Form(...),
    box_id: int = Form(...),
    confirmado: str = Form("false"),
    monto_seña: float = Form(0),
    forma_pago: str = Form("tarjeta"),
    descripcion: str = Form(""),
    recomendacion: str = Form(""),
    db: Session = Depends(get_db)
):
    hora_obj = time.fromisoformat(hora + ":00")
    fecha_obj = date.fromisoformat(fecha)

    turno_confirmado = services.box_esta_ocupado(db, box_id, fecha_obj, hora_obj, excluir_turno_id=turno_id)
    if turno_confirmado:
        turno = services.obtener_turno(db, turno_id)
        return templates.TemplateResponse("editar_turno.html", {
            "request": request,
            "turno": turno,
            "profesionales": services.listar_profesionales(db),
            "servicios": services.listar_servicios(db),
            "boxes": services.listar_boxes(db),
            "error": f"El box ya tiene un turno CONFIRMADO a las {hora}.",
        })

    services.editar_turno(db, turno_id, fecha_obj, hora_obj, profesional_id, box_id, servicio_id, confirmado == "true", monto_seña, forma_pago, descripcion, recomendacion)
    return RedirectResponse(f"/?fecha={fecha}", status_code=303)


# ------------------------
# ELIMINAR TURNO
# ------------------------

@router.get("/turnos/{turno_id}/eliminar")
def eliminar_turno(turno_id: int, fecha: str = None, db: Session = Depends(get_db)):
    services.eliminar_turno(db, turno_id)
    return RedirectResponse(f"/?fecha={fecha or services.hoy()}", status_code=303)


# ------------------------
# CONFIRMAR TURNO
# ------------------------

@router.post("/turnos/{turno_id}/confirmar")
def confirmar_turno(turno_id: int, fecha: str = Form(None), db: Session = Depends(get_db)):
    services.confirmar_turno(db, turno_id)
    return RedirectResponse(f"/?fecha={fecha or services.hoy()}", status_code=303)


# ------------------------
# SERVICIOS
# ------------------------

@router.get("/servicios")
def servicios_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("servicios.html", {
        "request": request,
        "servicios": services.listar_servicios(db)
    })


@router.post("/servicios/crear")
def crear_servicio(
    nombre: str = Form(...),
    duracion_min: int = Form(...),
    precio_tarjeta: float = Form(...),
    precio_contado: float = Form(...),
    capacidad_requerida: int = Form(...),
    db: Session = Depends(get_db)
):
    services.crear_servicio(db, nombre, duracion_min, precio_tarjeta, precio_contado, capacidad_requerida)
    return RedirectResponse("/servicios", status_code=303)


@router.get("/servicios/editar/{servicio_id}")
def editar_servicio_form(servicio_id: int, request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("editar_servicio.html", {
        "request": request,
        "servicio": services.obtener_servicio(db, servicio_id)
    })


@router.post("/servicios/editar/{servicio_id}")
def editar_servicio(
    servicio_id: int,
    nombre: str = Form(...),
    duracion_min: int = Form(...),
    precio_tarjeta: float = Form(...),
    precio_contado: float = Form(...),
    capacidad_requerida: int = Form(...),
    db: Session = Depends(get_db)
):
    services.editar_servicio(db, servicio_id, nombre, duracion_min, precio_tarjeta, precio_contado, capacidad_requerida)
    return RedirectResponse("/servicios", status_code=303)


@router.get("/servicios/eliminar/{servicio_id}")
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    services.eliminar_servicio(db, servicio_id)
    return RedirectResponse("/servicios", status_code=303)


# ------------------------
# BOXES
# ------------------------

@router.get("/boxes")
def boxes_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("boxes.html", {
        "request": request,
        "boxes": services.listar_boxes(db)
    })


@router.post("/boxes/crear")
def crear_box(nombre: str = Form(...), db: Session = Depends(get_db)):
    services.crear_box(db, nombre)
    return RedirectResponse("/boxes", status_code=303)


@router.get("/boxes/eliminar/{box_id}")
def eliminar_box(box_id: int, db: Session = Depends(get_db)):
    services.eliminar_box(db, box_id)
    return RedirectResponse("/boxes", status_code=303)


# ------------------------
# PROFESIONALES
# ------------------------

@router.get("/profesionales")
def profesionales_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("profesionales.html", {
        "request": request,
        "profesionales": services.listar_profesionales(db)
    })


@router.post("/profesionales/crear")
def crear_profesional(nombre: str = Form(...), db: Session = Depends(get_db)):
    services.crear_profesional(db, nombre)
    return RedirectResponse("/profesionales", status_code=303)


@router.get("/profesionales/eliminar/{profesional_id}")
def eliminar_profesional(profesional_id: int, db: Session = Depends(get_db)):
    services.eliminar_profesional(db, profesional_id)
    return RedirectResponse("/profesionales", status_code=303)


# ------------------------
# CLIENTES
# ------------------------

@router.get("/clientes")
def clientes(request: Request, q: str = Query(None), db: Session = Depends(get_db)):
    clientes = services.listar_clientes(db, busqueda=q)
    return templates.TemplateResponse("clientes.html", {
        "request": request,
        "clientes": clientes,
        "busqueda": q or "",
    })


@router.get("/clientes/{cliente_id}")
def cliente_detalle(cliente_id: int, request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("cliente_detalle.html", {
        "request": request,
        "cliente": services.obtener_cliente(db, cliente_id)
    })


@router.post("/clientes/{cliente_id}/tipo_piel")
def actualizar_tipo_piel(cliente_id: int, tipo_piel: str = Form(...), db: Session = Depends(get_db)):
    services.actualizar_tipo_piel(db, cliente_id, tipo_piel)
    return RedirectResponse(f"/clientes/{cliente_id}", status_code=303)



@router.post("/clientes/{cliente_id}/editar")
def editar_cliente(cliente_id: int, telefono: str = Form(""), tipo_piel: str = Form(""), db: Session = Depends(get_db)):
    services.editar_cliente(db, cliente_id, telefono, tipo_piel)
    return RedirectResponse(f"/clientes/{cliente_id}", status_code=303)

# ------------------------
# METRICAS
# ------------------------

@router.get("/metricas")
def metricas(request: Request, periodo: str = Query("esta_semana"), db: Session = Depends(get_db)):
    datos = services.metricas_generales(db, periodo=periodo)
    return templates.TemplateResponse("metricas.html", {
        "request": request,
        "datos": datos
    })