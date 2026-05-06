import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Ruta al modelo (mismo directorio que este archivo)
RUTA_MODELO = Path(__file__).parent / 'microbiota_modelo.pkl'

# Cargamos el modelo UNA SOLA VEZ cuando arranca la API
_modelo = joblib.load(RUTA_MODELO)

scaler_z             = _modelo['scaler_z']
gmm                  = _modelo['gmm']
iso_forest           = _modelo['iso_forest']
vector_ideal_Z       = _modelo['vector_ideal_Z']
pesos                = _modelo['pesos']
d_max                = _modelo['d_max']
cols_score           = _modelo['cols_score']
diccionario_clusters = _modelo['diccionario_clusters']
nombre_bristol       = _modelo['nombre_bristol']


def calcular_score(datos: dict) -> dict:

    # --- Variables derivadas ---
    imc_n         = datos['peso'] / (datos['estatura'] / 100) ** 2
    taquicardia_n = 1 if datos['fc'] > 90 else 0

    sexo = datos['sexo'].upper()
    if sexo == 'F':
        riesgo_cintura_n = 1 if datos['cintura'] >= 80 else 0
    elif sexo == 'M':
        riesgo_cintura_n = 1 if datos['cintura'] >= 94 else 0
    else:
        riesgo_cintura_n = 1 if datos['cintura'] >= 90 else 0

    if datos['p_3_1'] == 0:  # Postprandial
        if datos['glucosa'] < 140:          cat_glucosa_n = 0
        elif datos['glucosa'] < 200:        cat_glucosa_n = 1
        else:                               cat_glucosa_n = 2
    else:                    # Ayuno
        if datos['glucosa'] < 100:          cat_glucosa_n = 0
        elif datos['glucosa'] < 126:        cat_glucosa_n = 1
        else:                               cat_glucosa_n = 2

    diet_score_n        = (datos['p_3_8'] * 10) + (datos['p_3_6'] * 7) - (datos['p_3_5'] * 9) - (datos['p_3_12'] * 8)
    mal_sueno_n         = 5 - datos['p_6_7']
    lifestyle_score_n   = (datos['p_2_1'] * 8) - (datos['p_2_4'] * 7) - (datos['p_6_2'] * 9) - (datos['p_6_3'] * 5) - (datos['p_6_5'] * 7) - (datos['p_6_10'] * 4) - mal_sueno_n
    microbiota_stress_n = (datos['p_5_3'] * 10) + (datos['p_5_7'] * 9) + (datos['p_5_1'] * 4) + (datos['p_6_13'] * 5) + (datos['carga_sintomas'] * 5)

    # --- Empaquetado en orden exacto de cols_score ---
    mapa_valores = {
        'Microbiota_Stress' : microbiota_stress_n,
        'Categoria_Glucosa' : cat_glucosa_n,
        'Riesgo_cintura'    : riesgo_cintura_n,
        '5.4'               : datos['p_5_4'],
        'Diet_Score'        : diet_score_n,
        'Lifestyle_Score'   : lifestyle_score_n,
        'pH Salival'        : datos['ph_salival'],
        'IMC'               : imc_n,
        nombre_bristol      : datos['p_4_1'],
        '4.2'               : datos['p_4_2'],
        '1.3'               : datos['p_1_3'],
        'Taquicardia_reposo': taquicardia_n,
        'Temperatura (°C)'  : datos['temp'],
        'Fitzpatrick Scale' : datos['fitzpatrick']
    }

    fila      = [mapa_valores[col] for col in cols_score]
    df_nuevo  = pd.DataFrame([fila], columns=cols_score)

    # --- Predicción ---
    Z_nuevo     = scaler_z.transform(df_nuevo)
    distancia_n = np.sqrt(np.sum(pesos * (Z_nuevo[0] - vector_ideal_Z) ** 2))
    score_n     = max(0.0, min(100.0, 100 * (1 - (distancia_n / d_max))))

    df_modelo_nuevo = pd.DataFrame(Z_nuevo, columns=cols_score)
    df_modelo_nuevo['MicrobiotaScore_Weighted'] = score_n * 3

    cluster_n   = gmm.predict(df_modelo_nuevo)[0]
    perfil_n    = diccionario_clusters[cluster_n]
    anomalia_n  = iso_forest.predict(df_modelo_nuevo)[0]
    metabolic_risk_score_n = (imc_n * 0.3) + (riesgo_cintura_n * 2) + (cat_glucosa_n * 2)

    return {
        'microbiota_score' : round(score_n, 1),
        'perfil'           : perfil_n,
        'es_anomalia'      : bool(anomalia_n == -1),
        'imc'              : round(imc_n, 1),
        'diet_score'       : int(diet_score_n),
        'lifestyle_score'  : int(lifestyle_score_n),
        'microbiota_stress': int(microbiota_stress_n),
        'metabolic_risk_score': round(metabolic_risk_score_n, 1)
    }