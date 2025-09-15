from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import os

# -------------------------------
# MAPA DE ARCHIVOS
# -------------------------------
ARCHIVOS = {
    "lv": {  # lunes a viernes
        "ida": "data/TREN_LUNES_A_VIERNES_IDA.xls",
        "vuelta": "data/TREN_LUNES_A_VIERNES_VUELTA.xls"
    },
    "sd": {  # sábado y domingo
        "ida": "data/TREN_SABADO_DOMINGO_IDA.xls",
        "vuelta": "data/TREN_SABADO_DOMINGO_VUELTA.xls"
    }
}

# -------------------------------
# FUNCIÓN PARA LEER XLS → JSON
# -------------------------------
def cargar_horarios(path: str, dia: str, sentido: str):
    if not os.path.exists(path):
        return {"error": f"Archivo {path} no encontrado"}

    df = pd.read_excel(path)

    # La primera fila son las estaciones
    df.columns = df.iloc[0]
    df = df.drop(0).reset_index(drop=True)

    horarios = []
    for _, row in df.iterrows():
        salida = row.iloc[0]  # primera columna = hora base
        estaciones = row.to_dict()
        estaciones.pop(df.columns[0])  # quitamos la hora de salida

        horarios.append({
            "salida": str(salida),
            "estaciones": estaciones
        })

    nombre_dia = "Lunes a Viernes" if dia == "lv" else "Sábado y Domingo"
    return {
        "tren": nombre_dia,
        "sentido": sentido.capitalize(),
        "horarios": horarios
    }

# -------------------------------
# FUNCIÓN PARA LISTAR ESTACIONES
# -------------------------------
def listar_estaciones():
    estaciones_set = set()

    for dia, sentidos in ARCHIVOS.items():
        for sentido, path in sentidos.items():
            if not os.path.exists(path):
                continue
            df = pd.read_excel(path)
            df.columns = df.iloc[0]  # primera fila = estaciones
            estaciones = list(df.columns[1:])  # quitamos la primera col (hora salida)
            estaciones_set.update(estaciones)

    return sorted(estaciones_set)

# -------------------------------
# API FASTAPI
# -------------------------------
app = FastAPI(title="Horarios de Tren", version="1.1")

@app.get("/tren/{dia}/{sentido}")
def get_tren(dia: str, sentido: str):
    dia = dia.lower()
    sentido = sentido.lower()

    if dia not in ARCHIVOS or sentido not in ARCHIVOS[dia]:
        return JSONResponse(
            content={"error": "Parámetros inválidos. Usa /tren/{lv|sd}/{ida|vuelta}"},
            status_code=400
        )

    path = ARCHIVOS[di]()
