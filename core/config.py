
import os

class Settings:
    DB_URL = os.getenv("DB_URL", "sqlite:///./turnos.db")

settings = Settings()