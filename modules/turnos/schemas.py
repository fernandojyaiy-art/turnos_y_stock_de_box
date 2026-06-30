from pydantic import BaseModel
from datetime import date, time

class TurnoCreate(BaseModel):
    fecha: date
    hora_inicio: time
    nombre_cliente: str
    telefono: str | None = None
    servicio_id: int