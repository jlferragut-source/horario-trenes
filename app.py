from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
import os
from datetime import datetime

# -------------------------------
# ARCHIVOS DE HORARIOS
# -------------------------------
ARCHIVOS = {
    "lv": {  # Lunes a Viernes
        "ida": "data/TREN LUNES A VIERNES IDA.XLS",
        "vuelta": "data/TREN LUNES A VIERNES VUELTA.XLS"
    },
    "sd": {  # Sábado y Domingo
        "ida": "data/TREN SABADO DOMINGO IDA.XLS",
        "vuelta": "data/TREN SABADO DOMINGO VUELTA.XLS"
    }
}

# -------------------------------
# FUNCIÓN PARA LEER XLS A JSON
# -------------------------------
def leer_excel_a_json(path):
    if not os.path.exists(path):
        return {"error": f"Archivo {path} no encontrado"}
    df = pd.read_excel(path, header=0)
    df = df.astype(str)
    return df.to_dict(orient="records")

# -------------------------------
# CARGAR TODOS LOS HORARIOS AL INICIAR
# -------------------------------
DATOS = {}
for dia, sentidos in ARCHIVOS.items():
    DATOS[dia] = {}
    for sentido, path in sentidos.items():
        DATOS[dia][sentido] = leer_excel_a_json(path)

# -------------------------------
# FUNCIÓN PARA LISTAR TODAS LAS ESTACIONES
# -------------------------------
def listar_estaciones():
    estaciones_set = set()
    for dia, sentidos in DATOS.items():
        for sentido, horarios in sentidos.items():
            for fila in horarios:
                estaciones_set.update(fila.keys())
    return sorted(estaciones_set)

# -------------------------------
# API FASTAPI
# -------------------------------
