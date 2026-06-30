# Sistema de Gestión para Centro de Estética

Aplicación desarrollada en **Python + FastAPI + SQLAlchemy + SQLite** para administrar un centro de estética.

El proyecto nació para cubrir las necesidades reales de un gabinete de estética, permitiendo gestionar turnos, clientes, tratamientos, stock y métricas desde una única aplicación.

---

## Características

### Agenda de turnos

- Agenda diaria por profesionales.
- Administración de boxes.
- Turnos confirmados y pendientes.
- Control de seña.
- Cálculo automático del saldo restante.
- Distinción de precio contado / tarjeta.
- Servicios de uno o dos clientes.
- Descripción del tratamiento realizada.

---

### Clientes

- Historial de clientes.
- Teléfono.
- Tipo de piel.
- Observaciones del tratamiento.
- Edición rápida desde el turno.

---

### Servicios

- Alta, baja y modificación.
- Duración.
- Precio contado.
- Precio tarjeta.
- Cantidad de personas permitidas.

---

### Stock

- Gestión de productos.
- Registro de ventas.
- Control de inventario.
- Actualización automática del stock.

---

### Métricas

- Facturación de servicios.
- Facturación por ventas.
- Turnos realizados.
- Servicios más vendidos.
- Productos más vendidos.
- Clientes frecuentes.
- Clientes inactivos.

---

## Tecnologías

- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Jinja2
- HTML
- CSS

---

## Estructura

```
core/
modules/
    turnos/
    stock/
templates/
static/
main.py
```

---

## Instalación

Clonar el repositorio

```bash
git clone https://github.com/fernandojyaiy-art/turnos_y_stock_de_box.git
```

Ingresar

```bash
cd turnos_y_stock_de_box
```

Crear entorno virtual

```bash
python -m venv .venv
```

Activarlo

Windows

```bash
.venv\Scripts\activate
```

Instalar dependencias

```bash
pip install -r requirements.txt
```

Ejecutar

```bash
uvicorn main:app --reload
```

Abrir

```
http://127.0.0.1:8000
```

---

## Estado del proyecto

Proyecto en desarrollo activo.

Próximas funcionalidades previstas:

- Historial completo de tratamientos.
- Buscador avanzado.
- Reportes.
- Exportación de datos.
- Gestión de imágenes del cliente.
- Sistema de usuarios.
- Backup automático.

---

## Objetivo

Este proyecto fue desarrollado como software real para la administración de un gabinete de estética, buscando reemplazar el uso de planillas y simplificar el trabajo diario.

Actualmente continúa evolucionando mediante nuevas funcionalidades y mejoras de usabilidad.