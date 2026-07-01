from datetime import date, time, datetime, timedelta
from .models import Cliente, Servicio, Profesional, Box, Turno, Configuracion


# -----------------------
# FECHA
# -----------------------

def hoy():
    return date.today().isoformat()


# -----------------------
# CONFIGURACION
# -----------------------

def obtener_config(db, clave, default=None):
    c = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    return c.valor if c else default


def guardar_config(db, clave, valor):
    c = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if c:
        c.valor = str(valor)
    else:
        c = Configuracion(clave=clave, valor=str(valor))
        db.add(c)
    db.commit()


def monto_seña_default(db):
    return float(obtener_config(db, "seña_default", "15000"))


# -----------------------
# PROFESIONALES
# -----------------------

def listar_profesionales(db):
    return db.query(Profesional).all()


def crear_profesional(db, nombre):
    p = Profesional(nombre=nombre)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def eliminar_profesional(db, profesional_id):
    p = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    if p:
        db.delete(p)
        db.commit()


# -----------------------
# BOXES
# -----------------------

def listar_boxes(db):
    return db.query(Box).all()


def obtener_box(db, box_id):
    return db.query(Box).filter(Box.id == box_id).first()


def crear_box(db, nombre):
    b = Box(nombre=nombre)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def eliminar_box(db, box_id):
    b = obtener_box(db, box_id)
    if b:
        db.delete(b)
        db.commit()


def box_esta_ocupado(db, box_id, fecha, hora_inicio, excluir_turno_id=None):
    query = db.query(Turno).filter(
        Turno.box_id == box_id,
        Turno.fecha == fecha,
        Turno.hora_inicio == hora_inicio,
        Turno.confirmado == True
    )
    if excluir_turno_id:
        query = query.filter(Turno.id != excluir_turno_id)
    return query.first()


def box_tiene_pendiente(db, box_id, fecha, hora_inicio, excluir_turno_id=None):
    query = db.query(Turno).filter(
        Turno.box_id == box_id,
        Turno.fecha == fecha,
        Turno.hora_inicio == hora_inicio,
        Turno.confirmado == False
    )
    if excluir_turno_id:
        query = query.filter(Turno.id != excluir_turno_id)
    return query.first()


# -----------------------
# CLIENTES
# -----------------------

def listar_clientes(db, busqueda=None):
    query = db.query(Cliente)
    if busqueda:
        query = query.filter(
            Cliente.nombre.ilike(f"%{busqueda}%") |
            Cliente.apellido.ilike(f"%{busqueda}%") |
            Cliente.telefono.ilike(f"%{busqueda}%")
        )
    return query.order_by(Cliente.nombre).all()


def obtener_cliente(db, cliente_id):
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()


def crear_o_buscar_cliente(db, nombre, apellido, telefono):
    cliente = db.query(Cliente).filter(
        Cliente.nombre == nombre,
        Cliente.telefono == telefono
    ).first()
    if not cliente:
        cliente = Cliente(nombre=nombre, apellido=apellido, telefono=telefono)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    return cliente


def actualizar_tipo_piel(db, cliente_id, tipo_piel):
    cliente = obtener_cliente(db, cliente_id)
    if cliente:
        cliente.tipo_piel = tipo_piel
        db.commit()
    return cliente



def editar_cliente(db, cliente_id, telefono, tipo_piel):
    cliente = obtener_cliente(db, cliente_id)
    if cliente:
        cliente.telefono = telefono
        cliente.tipo_piel = tipo_piel
        db.commit()
    return cliente

# -----------------------
# SERVICIOS
# -----------------------

def listar_servicios(db):
    return db.query(Servicio).all()


def obtener_servicio(db, servicio_id):
    return db.query(Servicio).filter(Servicio.id == servicio_id).first()


def crear_servicio(db, nombre, duracion_min, precio_tarjeta, precio_contado, capacidad):
    s = Servicio(
        nombre=nombre,
        duracion_min=duracion_min,
        precio_tarjeta=precio_tarjeta,
        precio_contado=precio_contado,
        capacidad_requerida=capacidad
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def editar_servicio(db, servicio_id, nombre, duracion_min, precio_tarjeta, precio_contado, capacidad):
    s = obtener_servicio(db, servicio_id)
    if s:
        s.nombre = nombre
        s.duracion_min = duracion_min
        s.precio_tarjeta = precio_tarjeta
        s.precio_contado = precio_contado
        s.capacidad_requerida = capacidad
        db.commit()
    return s


def eliminar_servicio(db, servicio_id):
    s = obtener_servicio(db, servicio_id)
    if s:
        db.delete(s)
        db.commit()


# -----------------------
# PRECIO Y SALDO
# -----------------------

def precio_turno(turno):
    """Precio según forma de pago. Si no tiene forma de pago aún, devuelve tarjeta."""
    if turno.forma_pago == "efectivo":
        return turno.servicio.precio_contado
    return turno.servicio.precio_tarjeta


def saldo_turno(turno):
    """Cuánto le queda por pagar al cliente cuando viene."""
    return precio_turno(turno) - (turno.monto_seña or 0)


# -----------------------
# TURNOS
# -----------------------

def obtener_turno(db, turno_id):
    return db.query(Turno).filter(Turno.id == turno_id).first()


def crear_turno(db, fecha, hora_inicio, cliente_id, servicio_id, profesional_id,
                box_id=None, confirmado=False, monto_seña=0, forma_pago=None):
    turno = Turno(
        fecha=fecha,
        hora_inicio=hora_inicio,
        cliente_id=cliente_id,
        servicio_id=servicio_id,
        profesional_id=profesional_id,
        box_id=box_id,
        confirmado=confirmado,
        monto_seña=monto_seña,
        forma_pago=forma_pago
    )
    db.add(turno)
    db.commit()
    db.refresh(turno)
    return turno


def editar_turno(db, turno_id, fecha, hora_inicio, profesional_id, box_id,
                 servicio_id, confirmado, monto_seña=0, forma_pago=None, descripcion="", recomendacion=""):
    turno = obtener_turno(db, turno_id)
    if turno:
        turno.fecha = fecha
        turno.hora_inicio = hora_inicio
        turno.profesional_id = profesional_id
        turno.box_id = box_id
        turno.servicio_id = servicio_id
        turno.confirmado = confirmado
        turno.monto_seña = monto_seña
        turno.forma_pago = forma_pago
        turno.descripcion = descripcion
        turno.recomendacion = recomendacion
        db.commit()
    return turno


def eliminar_turno(db, turno_id):
    turno = obtener_turno(db, turno_id)
    if turno:
        db.delete(turno)
        db.commit()


def confirmar_turno(db, turno_id):
    turno = obtener_turno(db, turno_id)
    if turno:
        turno.confirmado = True
        db.commit()
    return turno


# -----------------------
# GRILLA
# -----------------------

def bloque_esta_en_curso(turno, hora_bloque):
    inicio = datetime.combine(date.today(), turno.hora_inicio)
    fin = inicio + timedelta(minutes=turno.servicio.duracion_min)
    bloque = datetime.combine(date.today(), hora_bloque)
    return inicio < bloque < fin


def armar_grilla(db, fecha):
    profesionales = listar_profesionales(db)
    grilla = []

    for minutos_totales in range(10 * 60, 19 * 60 + 1, 30):
        hora = minutos_totales // 60
        minuto = minutos_totales % 60
        hora_time = time(hora, minuto, 0)
        hora_str = f"{hora:02d}:{minuto:02d}"

        bloques = []
        for p in profesionales:
            turnos = db.query(Turno).filter(
                Turno.fecha == fecha,
                Turno.hora_inicio == hora_time,
                Turno.profesional_id == p.id
            ).all()

            todos_los_turnos = db.query(Turno).filter(
                Turno.fecha == fecha,
                Turno.profesional_id == p.id
            ).all()

            en_curso = any(bloque_esta_en_curso(t, hora_time) for t in todos_los_turnos)

            bloques.append({
                "hora": hora_str,
                "profesional": p.nombre,
                "profesional_id": p.id,
                "turnos": turnos,
                "disponible": len(turnos) == 0 and not en_curso,
                "en_curso": en_curso,
            })

        grilla.append({"hora": hora_str, "bloques": bloques})

    return grilla


# -----------------------
# METRICAS
# -----------------------

def calcular_periodo(periodo):
    """
    Recibe un string con el período y devuelve (desde, hasta, etiqueta).
    Así la ruta puede pedir cualquier período y siempre obtenemos
    las fechas correctas sin repetir lógica.
    """
    hoy = date.today()

    if periodo == "semana_pasada":
        # Lunes de la semana pasada
        inicio = hoy - timedelta(days=hoy.weekday() + 7)
        fin = inicio + timedelta(days=6)
        etiqueta = "Semana pasada"

    elif periodo == "este_mes":
        inicio = hoy.replace(day=1)
        fin = hoy
        etiqueta = "Este mes"

    elif periodo == "mes_pasado":
        # Primer dia del mes pasado
        primer_dia_mes_actual = hoy.replace(day=1)
        fin = primer_dia_mes_actual - timedelta(days=1)
        inicio = fin.replace(day=1)
        etiqueta = "Mes pasado"

    else:  # esta_semana (default)
        inicio = hoy - timedelta(days=hoy.weekday())
        fin = hoy
        etiqueta = "Esta semana"

    return inicio, fin, etiqueta


def metricas_generales(db, periodo="esta_semana"):
    from modules.stock.models import Venta, Producto
    from sqlalchemy import func

    hoy_fecha = date.today()
    desde, hasta, etiqueta_periodo = calcular_periodo(periodo)

    def turnos_periodo(d, h):
        return db.query(Turno).filter(
            Turno.fecha >= d,
            Turno.fecha <= h,
            Turno.confirmado == True
        ).all()

    # Período seleccionado
    turnos_periodo_sel = turnos_periodo(desde, hasta)

    # Hoy siempre fijo para referencia rápida
    turnos_hoy = turnos_periodo(hoy_fecha, hoy_fecha)

    def facturacion(turnos):
        return sum(precio_turno(t) for t in turnos)

    def ventas_rango(d, h):
        return db.query(Venta).filter(
            Venta.fecha >= d,
            Venta.fecha <= h
        ).all()

    ventas_periodo_sel = ventas_rango(desde, hasta)
    ventas_hoy = ventas_rango(hoy_fecha, hoy_fecha)

    def facturacion_ventas(ventas):
        return sum(v.producto.precio * v.cantidad for v in ventas)

    servicios_top = (
        db.query(Servicio.nombre, func.count(Turno.id).label("cantidad"))
        .join(Turno, Turno.servicio_id == Servicio.id)
        .filter(Turno.confirmado == True, Turno.fecha >= desde, Turno.fecha <= hasta)
        .group_by(Servicio.nombre)
        .order_by(func.count(Turno.id).desc())
        .limit(5).all()
    )

    productos_top = (
        db.query(Producto.nombre, func.sum(Venta.cantidad).label("total"))
        .join(Venta, Venta.producto_id == Producto.id)
        .filter(Venta.fecha >= desde, Venta.fecha <= hasta)
        .group_by(Producto.nombre)
        .order_by(func.sum(Venta.cantidad).desc())
        .limit(5).all()
    )

    clientes_top = (
        db.query(Cliente.nombre, Cliente.apellido, func.count(Turno.id).label("visitas"))
        .join(Turno, Turno.cliente_id == Cliente.id)
        .filter(Turno.confirmado == True)
        .group_by(Cliente.id)
        .order_by(func.count(Turno.id).desc())
        .limit(5).all()
    )

    hace_30_dias = hoy_fecha - timedelta(days=30)
    todos_clientes = db.query(Cliente).all()
    clientes_inactivos = []
    for c in todos_clientes:
        ultimo = (
            db.query(Turno)
            .filter(Turno.cliente_id == c.id, Turno.confirmado == True)
            .order_by(Turno.fecha.desc())
            .first()
        )
        if ultimo and ultimo.fecha < hace_30_dias:
            clientes_inactivos.append({
                "nombre": f"{c.nombre} {c.apellido}",
                "telefono": c.telefono,
                "ultimo_turno": ultimo.fecha,
                "dias": (hoy_fecha - ultimo.fecha).days
            })

    clientes_inactivos.sort(key=lambda x: x["dias"], reverse=True)

    return {
        # Período seleccionado
        "periodo": periodo,
        "etiqueta_periodo": etiqueta_periodo,
        "desde": desde,
        "hasta": hasta,
        "servicios_periodo": facturacion(turnos_periodo_sel),
        "turnos_periodo": len(turnos_periodo_sel),
        "productos_periodo": facturacion_ventas(ventas_periodo_sel),
        # Hoy siempre
        "servicios_hoy": facturacion(turnos_hoy),
        "turnos_hoy": len(turnos_hoy),
        "productos_hoy": facturacion_ventas(ventas_hoy),
        # Rankings filtrados por período
        "servicios_top": servicios_top,
        "productos_top": productos_top,
        "clientes_top": clientes_top,
        "clientes_inactivos": clientes_inactivos[:10],
    }