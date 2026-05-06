from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from uuid import uuid4
from schemas import DatosPaciente, ResultadoPaciente
from modelo import calcular_score
from database import coleccion_resultados

app = FastAPI(
    title="Microbiota Score API",
    description="Recibe datos clínicos y devuelve el perfil de salud intestinal.",
    version="1.0.0"
)

@app.get("/")
def raiz():
    return {"status": "ok", "mensaje": "Microbiota Score API funcionando"}

@app.post("/predecir", response_model=ResultadoPaciente)
async def predecir(datos: DatosPaciente):
    try:
        resultado = calcular_score(datos.dict())

        # Generamos un ID único para cada paciente nuevo
        # Formato: PAC-xxxxxxxx (fácil de leer y compartir)
        id_generado = f"PAC-{uuid4().hex[:8].upper()}"

        documento = {
            'id_paciente'         : id_generado,
            **resultado,
            'fecha'               : datetime.now(timezone.utc)
        }

        await coleccion_resultados.insert_one(documento)

        return {'id_paciente': id_generado, **resultado}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resultados")
async def obtener_resultados():
    try:
        cursor = coleccion_resultados.find(
            {},
            {"_id": 0}
        ).sort("fecha", -1).limit(20)

        resultados = await cursor.to_list(length=20)
        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resultados/{id_paciente}")
async def obtener_por_id(id_paciente: str):
    """Busca el resultado de un paciente por su ID"""
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
        raise HTTPException(status_code=500, detail=str(e))