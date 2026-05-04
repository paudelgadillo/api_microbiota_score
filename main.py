from fastapi import FastAPI, HTTPException
from schemas import DatosPaciente, ResultadoPaciente
from modelo import calcular_score

app = FastAPI(
    title="Microbiota Score API",
    description="Recibe datos clínicos y devuelve el perfil de salud intestinal del paciente.",
    version="1.0.0"
)


@app.get("/")
def raiz():
    return {"status": "ok", "mensaje": "Microbiota Score API funcionando"}


@app.post("/predecir", response_model=ResultadoPaciente)
def predecir(datos: DatosPaciente):
    try:
        resultado = calcular_score(datos.dict())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))