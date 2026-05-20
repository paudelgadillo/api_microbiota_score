import os
import ssl
import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB  = os.getenv("MONGODB_DB")

# Usamos el certificado de certifi para resolver el problema SSL en Windows
cliente = AsyncIOMotorClient(
    MONGODB_URL,
    tls=True,
    tlsCAFile=certifi.where()
)

db = cliente[MONGODB_DB]
coleccion_resultados = db["resultados"]