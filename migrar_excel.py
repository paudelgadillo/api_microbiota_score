import asyncio
import pandas as pd
from datetime import datetime, timezone
from database import db

RUTA_TSNE = 'datos_tsne_exactos.csv'

def transformar_anomalia(valor: str) -> bool:
    if isinstance(valor, str):
        return 'atípico' in valor.lower() or 'atipico' in valor.lower()
    return False

async def migrar_graficas():
    print("Leyendo coordenadas t-SNE exactas del notebook...")
    df = pd.read_csv(RUTA_TSNE)
    print(f"  {len(df)} registros encontrados.")
    print(df.head())

    coleccion_graficas = db["graficas"]
    await coleccion_graficas.drop()

    documentos = []
    for _, fila in df.iterrows():
        documentos.append({
            'id_paciente'     : str(fila['id_match']),
            'perfil'          : str(fila['perfil']),
            'es_anomalia'     : transformar_anomalia(str(fila['anomalia'])),
            'anomalia_texto'  : str(fila['anomalia']),
            'microbiota_score': float(fila['microbiota_score']),
            'tsne_x'          : float(fila['tsne_x']),
            'tsne_y'          : float(fila['tsne_y']),
        })

    await coleccion_graficas.insert_many(documentos)
    print(f"\n{len(documentos)} registros migrados a colección 'graficas'.")
    print("Verifica en Atlas que los valores tsne_x y tsne_y coincidan con el notebook.")

if __name__ == "__main__":
    asyncio.run(migrar_graficas())