from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.database import Base, engine

from modules.turnos import models as turnos_models  # registra tablas de turnos
from modules.stock import models as stock_models    # registra tablas de stock

from modules.turnos.routes import router as turnos_router
from modules.stock.routes import router as stock_router

app = FastAPI()

# Archivos estáticos (CSS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# DB: crea todas las tablas que no existan
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(turnos_router)
app.include_router(stock_router)