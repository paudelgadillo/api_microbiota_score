from pydantic import BaseModel, Field
from typing import Literal

class DatosPaciente(BaseModel):
    # Fase 1: Antropometría
    peso:         float = Field(..., example=70.0)
    estatura:     float = Field(..., example=165.0)
    cintura:      float = Field(..., example=85.0)
    sexo:         Literal['M', 'F'] = Field(..., example='F')
    fc:           int   = Field(..., example=75)
    glucosa:      float = Field(..., example=95.0)
    ph_salival:   float = Field(..., example=7.0)
    temp:         float = Field(..., example=36.5)
    fitzpatrick:  int   = Field(..., ge=1, le=6, example=3)

    # Fase 2: Hábitos
    p_1_3:  int = Field(..., ge=0, le=1,  example=0,  description="Cesarea: 0=No, 1=Si")
    p_2_1:  int = Field(..., ge=0, le=3,  example=2,  description="Ejercicio: 0=Nunca, 1=1-2d, 2=3-4d, 3=5+d")
    p_2_4:  int = Field(..., ge=0, le=3,  example=1,  description="Sedentarismo: 0=<4h, 1=4-6h, 2=7-9h, 3=+9h")
    p_6_7:  int = Field(..., ge=1, le=5,  example=4,  description="Calidad sueno: 1=Muy mala, 5=Excelente")
    p_6_2:  int = Field(..., ge=1, le=4,  example=2,  description="Estres: 1=Bajo, 4=Muy alto")
    p_6_3:  int = Field(..., ge=0, le=1,  example=0,  description="Fuma: 0=No, 1=Si")
    p_6_5:  int = Field(..., ge=0, le=1,  example=0,  description="Alcohol: 0=No, 1=Si")
    p_6_10: int = Field(..., ge=0, le=3,  example=0,  description="Enjuague bucal: 0=No, 1=Ocasional, 2=Varias/sem, 3=Diario")

    # Fase 3: Dieta y digestión
    p_3_1:  int = Field(..., ge=0, le=3,  example=1,  description="Ayuno: 0=<8h, 1=8-10h, 2=10-12h, 3=+12h")
    p_3_8:  int = Field(..., ge=0, le=3,  example=3,  description="Fibra: 0=Nunca, 1=1-2/sem, 2=3-5/sem, 3=Diario")
    p_3_6:  int = Field(..., ge=0, le=3,  example=1,  description="Fermentados: 0=Nunca, 1=Rara vez, 2=Ocasional, 3=Frecuente")
    p_3_5:  int = Field(..., ge=0, le=3,  example=1,  description="Ultraprocesados: 0=Nunca, 1=1-2/sem, 2=3-4/sem, 3=5+")
    p_3_12: int = Field(..., ge=0, le=3,  example=0,  description="Edulcorantes: 0=No, 1=Ocasional, 2=Varias/sem, 3=Diario")
    p_4_1:  int = Field(..., ge=1, le=7,  example=4,  description="Bristol: 1=Duro, 4=Ideal, 7=Liquido")
    p_4_2:  int = Field(..., ge=0, le=3,  example=1,  description="Evacuacion: 0=<3/sem, 1=1/dia, 2=2-3/dia, 3=+3/dia")

    # Fase 4: Alertas clínicas
    p_5_4:  int = Field(..., ge=0, le=1,  example=0,  description="Enfermedad digestiva: 0=No, 1=Si")
    p_5_1:  int = Field(..., ge=1, le=3,  example=1,  description="Enfermedades/año: 1=1vez, 2=2-3, 3=4+")
    p_5_3:  int = Field(..., ge=0, le=1,  example=0,  description="Antibioticos: 0=No, 1=Si")
    p_5_7:  int = Field(..., ge=0, le=1,  example=0,  description="Infeccion GI: 0=No, 1=Si")
    p_6_13: int = Field(..., ge=0, le=3,  example=1,  description="Digestivo por estres: 0=Nunca, 1=A veces, 2=Frecuente, 3=Diario")
    carga_sintomas: int = Field(..., ge=0, le=7, example=2, description="Total de sintomas frecuentes (0 a 7)")


class ResultadoPaciente(BaseModel):
    microbiota_score:  float
    perfil:            str
    es_anomalia:       bool
    imc:               float
    diet_score:        int
    lifestyle_score:   int
    microbiota_stress: int