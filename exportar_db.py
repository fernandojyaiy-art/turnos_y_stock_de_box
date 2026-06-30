import json
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///turnos.db")

with engine.connect() as conn:
    datos = {}
    tablas = ["clientes", "profesionales", "boxes", "servicios",
              "productos", "turnos", "ventas", "configuracion"]

    for tabla in tablas:
        filas = conn.execute(text(f"SELECT * FROM {tabla}")).fetchall()
        datos[tabla] = [dict(f._mapping) for f in filas]
        print(f"  {tabla}: {len(filas)} registros exportados")

with open("backup_datos.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2, default=str)

print()
print("Listo! Datos guardados en backup_datos.json")