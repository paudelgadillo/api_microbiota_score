from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from schemas import DatosPaciente, ResultadoPaciente
from modelo import calcular_score
from database import coleccion_resultados

app = FastAPI(
    title="Microbiota Score API",
    description="Recibe datos clínicos y devuelve el perfil de salud intestinal del paciente.",
    version="1.0.0"
)


@app.get("/")
def raiz():
    return {"status": "ok", "mensaje": "Microbiota Score API funcionando"}


@app.post("/predecir", response_model=ResultadoPaciente)
async def predecir(datos: DatosPaciente):
    try:
        # 1. Calculamos el score con el modelo
        resultado = calcular_score(datos.dict())

        # 2. Agregamos fecha y hora exacta en UTC
        documento = {
            **resultado,
            "fecha": datetime.now(timezone.utc)
        }

        # 3. Guardamos en MongoDB Atlas
        await coleccion_resultados.insert_one(documento)

        # 4. Devolvemos el resultado al cliente (sin el _id de mongo)
        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resultados")
async def obtener_resultados():
    """Endpoint extra para ver los últimos 20 resultados guardados"""
    try:
        cursor = coleccion_resultados.find(
            {},
            {"_id": 0}  # Excluimos el _id de MongoDB para que no rompa el JSON
        ).sort("fecha", -1).limit(20)

        resultados = await cursor.to_list(length=20)
        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))