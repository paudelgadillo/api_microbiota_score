import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB  = os.getenv("MONGODB_DB")

cliente = AsyncIOMotorClient(MONGODB_URL)
db      = cliente[MONGODB_DB]

coleccion_resultados = db["resultados"]