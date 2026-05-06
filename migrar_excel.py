import asyncio
import pandas as pd
from datetime import datetime, timezone
from database import coleccion_resultados

RUTA_EXCEL = 'Reporte_Modelo_Biomatematico_20260505_160701.xlsx'

def transformar_anomalia(valor: str) -> bool:
    """Convierte el texto de Anomalia a booleano"""
    if isinstance(valor, str):
        return 'atípico' in valor.lower() or 'atipico' in valor.lower()
    return False

async def migrar():
    print("Leyendo Excel...")
    df = pd.read_excel(RUTA_EXCEL)

    documentos = []
    for _, fila in df.iterrows():
        doc = {
            'id_paciente'         : str(fila['id_match']),  # ← usa su número real
            'microbiota_score'    : float(fila['Indice_Microbiota']),
            'perfil'              : str(fila['Perfil_GMM']),
            'es_anomalia'         : transformar_anomalia(str(fila['Anomalia'])),
            'imc'                 : float(fila['IMC']),
            'diet_score'          : int(fila['Diet_Score']),
            'lifestyle_score'     : int(fila['Lifestyle_Score']),
            'microbiota_stress'   : int(fila['Microbiota_Stress']),
            'metabolic_risk_score': float(fila['Metabolic_Risk_Score']),
            'fecha'               : datetime.now(timezone.utc)
        }
        documentos.append(doc)

    print(f"Migrando {len(documentos)} registros a MongoDB...")
    await coleccion_resultados.insert_many(documentos)
    print("Migración completada exitosamente.")

if __name__ == "__main__":
    asyncio.run(migrar())