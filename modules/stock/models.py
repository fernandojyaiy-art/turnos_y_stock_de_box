from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

    ventas = relationship("Venta", back_populates="producto")


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    cantidad = Column(Integer, default=1)

    # ForeignKey usa el nombre de la TABLA (string), no el nombre de la clase Python
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)

    cliente = relationship("Cliente", back_populates="ventas")
    producto = relationship("Producto", back_populates="ventas")