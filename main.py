from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from schemas import DatosPaciente, ResultadoPaciente
from modelo import calcular_score
from database import coleccion_resultados, db
from sklearn.manifold import TSNE
import numpy as np
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from auth import verificar_credenciales, crear_token, verificar_token


app = FastAPI(
    title="Microbiota Score API",
    description="Recibe datos clínicos y devuelve el perfil de salud intestinal.",
    version="1.0.0"
)

# CORS — permite que Next.js se comunique con FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def raiz():
    return {"status": "ok", "mensaje": "Microbiota Score API funcionando"}


@app.post("/predecir", response_model=ResultadoPaciente)
async def predecir(datos: DatosPaciente):
    try:
        resultado = calcular_score(datos.dict())

        # Busca el ID numérico más alto existente y suma 1
        pipeline = [
            {"$addFields": {"id_numerico": {"$toInt": "$id_paciente"}}},
            {"$sort": {"id_numerico": -1}},
            {"$limit": 1}
        ]
        cursor = coleccion_resultados.aggregate(pipeline)
        ultimo = await cursor.to_list(length=1)

        if ultimo:
            siguiente = int(ultimo[0]["id_paciente"]) + 1
        else:
            siguiente = 112
        id_generado = str(siguiente)

        # Extraemos los z_scores antes de guardar el resultado principal
        z_scores = resultado.pop('_z_scores')

        documento_resultado = {
            'id_paciente': id_generado,
            **resultado,
            'fecha': datetime.now(timezone.utc)
        }
        await coleccion_resultados.insert_one(documento_resultado)

        coleccion_zscores = db["zscores"]
        await coleccion_zscores.insert_one({
            'id_paciente'     : id_generado,
            'perfil'          : resultado['perfil'],
            'es_anomalia'     : resultado['es_anomalia'],
            'microbiota_score': resultado['microbiota_score'],
            'z_scores'        : z_scores,
            'fecha'           : datetime.now(timezone.utc)
        })

        # ── Opción C: posicionar el nuevo paciente en la gráfica ──────────────
        # Sin recalcular t-SNE para no mover a los demás pacientes.
        # Se calcula el centroide del perfil del nuevo paciente y se le
        # agrega un pequeño ruido reproducible basado en su ID.
        coleccion_graficas = db["graficas"]

        mismo_perfil = await coleccion_graficas.find(
            {"perfil": resultado["perfil"]},
            {"tsne_x": 1, "tsne_y": 1, "_id": 0}
        ).to_list(length=1000)

        if mismo_perfil:
            cx = np.mean([d["tsne_x"] for d in mismo_perfil])
            cy = np.mean([d["tsne_y"] for d in mismo_perfil])
            # Seed basado en el ID para que el ruido sea siempre el mismo
            # si se vuelve a correr con el mismo paciente
            rng    = np.random.default_rng(int(id_generado))
            tsne_x = float(cx + rng.normal(0, 1.5))
            tsne_y = float(cy + rng.normal(0, 1.5))
        else:
            # Fallback: si no hay pacientes con ese perfil todavía
            tsne_x, tsne_y = 0.0, 0.0

        await coleccion_graficas.insert_one({
            'id_paciente'     : id_generado,
            'perfil'          : resultado['perfil'],
            'es_anomalia'     : resultado['es_anomalia'],
            'microbiota_score': resultado['microbiota_score'],
            'tsne_x'          : tsne_x,
            'tsne_y'          : tsne_y,
        })
        # ─────────────────────────────────────────────────────────────────────

        return {'id_paciente': id_generado, **resultado}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resultados")
async def obtener_resultados():
    try:
        cursor = coleccion_resultados.find(
            {},
            {"_id": 0}
        ).sort("fecha", -1).limit(200)

        resultados = await cursor.to_list(length=200)
        return resultados

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resultados/{id_paciente}")
async def obtener_por_id(id_paciente: str):
    try:
        resultado = await coleccion_resultados.find_one(
            {"id_paciente": id_paciente},
            {"_id": 0}
        )
        if not resultado:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graficas")
async def obtener_graficas():
    try:
        coleccion_graficas = db["graficas"]
        cursor = coleccion_graficas.find({}, {"_id": 0})
        datos  = await cursor.to_list(length=500)

        if len(datos) == 0:
            raise HTTPException(
                status_code=400,
                detail="No hay datos de gráficas. Corre el script de migración primero."
            )

        return datos

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
# Agrega esto después de crear el app
security = HTTPBearer()

# Schema para el login
class LoginRequest(BaseModel):
    username: str
    password: str

# Dependencia reutilizable para proteger endpoints si lo necesitas después
async def requerir_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = verificar_token(credentials.credentials)
    if not payload or payload.get("rol") != "admin":
        raise HTTPException(status_code=401, detail="No autorizado")
    return payload

# Endpoints de autenticación
@app.post("/auth/login")
async def login_admin(datos: LoginRequest):
    if not verificar_credenciales(datos.username, datos.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = crear_token()
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/verificar")
async def verificar_sesion(payload: dict = Depends(requerir_admin)):
    return {"valid": True, "user": payload.get("sub")}    