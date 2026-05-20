import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY     = os.getenv("SECRET_KEY", "cambia_esto")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
ALGORITHM      = "HS256"
EXPIRE_HORAS   = 8

def verificar_credenciales(username: str, password: str) -> bool:
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def crear_token() -> str:
    expira  = datetime.now(timezone.utc) + timedelta(hours=EXPIRE_HORAS)
    payload = {"sub": ADMIN_USERNAME, "rol": "admin", "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None