from datetime import date
from .models import Producto, Venta


# -----------------------
# PRODUCTOS
# -----------------------

def listar_productos(db):
    return db.query(Producto).order_by(Producto.nombre).all()


def obtener_producto(db, producto_id):
    return db.query(Producto).filter(Producto.id == producto_id).first()


def crear_producto(db, nombre, precio, stock):
    p = Producto(nombre=nombre, precio=precio, stock=stock)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def editar_producto(db, producto_id, nombre, precio, stock):
    p = obtener_producto(db, producto_id)
    if p:
        p.nombre = nombre
        p.precio = precio
        p.stock = stock
        db.commit()
    return p


def eliminar_producto(db, producto_id):
    p = obtener_producto(db, producto_id)
    if p:
        db.delete(p)
        db.commit()


# -----------------------
# VENTAS
# -----------------------

def registrar_venta(db, cliente_id, producto_id, cantidad):
    # Verificamos que haya stock suficiente
    producto = obtener_producto(db, producto_id)
    if not producto or producto.stock < cantidad:
        return None, "Stock insuficiente"

    venta = Venta(
        fecha=date.today(),
        cliente_id=cliente_id,
        producto_id=producto_id,
        cantidad=cantidad
    )
    db.add(venta)

    # Descontamos del stock
    producto.stock -= cantidad

    db.commit()
    db.refresh(venta)
    return venta, None


def listar_ventas_cliente(db, cliente_id):
    return db.query(Venta).filter(
        Venta.cliente_id == cliente_id
    ).order_by(Venta.fecha.desc()).all()