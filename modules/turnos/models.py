from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Float, Index, Boolean
from sqlalchemy.orm import relationship
from core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String)
    telefono = Column(String)
    tipo_piel = Column(String, nullable=True)

    turnos = relationship("Turno", back_populates="cliente")
    ventas = relationship("Venta", back_populates="cliente")


class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    duracion_min = Column(Integer, nullable=False)
    precio_tarjeta = Column(Float, nullable=False)
    precio_contado = Column(Float, nullable=False)
    capacidad_requerida = Column(Integer, default=1)


class Profesional(Base):
    __tablename__ = "profesionales"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    turnos = relationship("Turno", back_populates="profesional")


class Box(Base):
    __tablename__ = "boxes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    turnos = relationship("Turno", back_populates="box")


class Configuracion(Base):
    """Tabla clave-valor para settings configurables desde la app."""
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True)
    clave = Column(String, unique=True, nullable=False)
    valor = Column(String, nullable=False)


class Turno(Base):
    __tablename__ = "turnos"

    __table_args__ = (
        Index("idx_turno_fecha_hora", "fecha", "hora_inicio"),
    )

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)

    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False)
    box_id = Column(Integer, ForeignKey("boxes.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    confirmado = Column(Boolean, default=False, nullable=False)

    # Forma de pago del saldo cuando viene el cliente
    forma_pago = Column(String, nullable=True)  # "efectivo" o "tarjeta", se completa cuando viene

    # Seña: si confirmado=True, monto_seña tiene lo que abonó
    monto_seña = Column(Float, default=0, nullable=False)
    descripcion = Column(String, nullable=True)
    recomendacion = Column(String, nullable=True)

    cliente = relationship("Cliente", back_populates="turnos")
    servicio = relationship("Servicio")
    profesional = relationship("Profesional", back_populates="turnos")
    box = relationship("Box", back_populates="turnos")