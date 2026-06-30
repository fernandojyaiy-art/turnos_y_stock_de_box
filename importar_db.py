import json
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///turnos.db")

with open("backup_datos.json", "r", encoding="utf-8") as f:
    datos = json.load(f)

with engine.connect() as conn:
    orden = ["clientes", "profesionales", "boxes", "servicios",
             "productos", "configuracion", "turnos", "ventas"]

    for tabla in orden:
        filas = datos.get(tabla, [])
        if not filas:
            print(f"  {tabla}: sin datos, saltando")
            continue

        for fila in filas:
            if tabla == "turnos" and "descripcion" not in fila:
                fila["descripcion"] = ""

            columnas = ", ".join(fila.keys())
            valores = ", ".join([f":{k}" for k in fila.keys()])
            sql = f"INSERT OR IGNORE INTO {tabla} ({columnas}) VALUES ({valores})"
            conn.execute(text(sql), fila)

        conn.commit()
        print(f"  {tabla}: {len(filas)} registros importados")

print()
print("Listo! Todos los datos fueron restaurados.")