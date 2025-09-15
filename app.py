from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import os

# -------------------------------
# MAPA DE ARCHIVOS
# -------------------------------
ARCHIVOS = {
    "lv": {  # lunes a viernes
        "ida": "data/TREN_LUNES_A_VIERNES_IDA.XLS",
        "vuelta": "data/TREN_LUNES_A_VIERNES_VUELTA.XLS"
    },
    "sd": {  # sábado y domingo
        "ida": "data/TREN_SABADO_DOMINGO_IDA.XLS",
        "vuelta": "data/TREN_SABADO_DOMINGO_VUELTA.XLS"
    }
}

# -------------------------------
# Cargar todos los horarios al iniciar
# -------------------------------
def leer_excel_a_json(path):
    if not os.path.exists(path):
        return {"error": f"Archivo {path} no encontrado"}

    df = pd.read_excel(path, header=0)
    df = df.astype(str)
    horarios = df.to_dict(orient="records")
    return horarios

# Diccionario para almacenar todos los horarios
DATOS = {}
for dia, sentidos in ARCHIVOS.items():
    DATOS[dia] = {}
    for sentido, path in sentidos.items():
        DATOS[dia][sentido] = leer_excel_a_json(path)

# -------------------------------
# Función para listar todas las estaciones
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
app = FastAPI(title="Horarios de Tren", version="2.0")

@app.get("/tren/{dia}/{sentido}")
def get_tren(dia: str, sentido: str):
    dia = dia.lower()
    sentido = sentido.lower()

    if dia not in DATOS or sentido not in DATOS[dia]:
        return JSONResponse(
            content={"error": "Parámetros inválidos. Usa /tren/{lv|sd}/{ida|vuelta}"},
            status_code=400
        )

    return JSONResponse(content={
        "tren": "Lunes a Viernes" if dia=="lv" else "Sábado y Domingo",
        "sentido": sentido.capitalize(),
        "horarios": DATOS[dia][sentido]
    })

@app.get("/tren/estaciones")
def get_estaciones():
    return JSONResponse(content={"estaciones": listar_estaciones()})

# -------------------------------
# TEST LOCAL
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
