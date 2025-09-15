from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
import os
from datetime import datetime

# -------------------------------
# ARCHIVOS DE HORARIOS
# -------------------------------
ARCHIVOS = {
    "lv": {
        "ida": "data/TREN LUNES A VIERNES IDA.XLS",
        "vuelta": "data/TREN LUNES A VIERNES VUELTA.XLS"
    },
    "sd": {
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
# CARGAR HORARIOS
# -------------------------------
DATOS = {}
for dia, sentidos in ARCHIVOS.items():
    DATOS[dia] = {}
    for sentido, path in sentidos.items():
        DATOS[dia][sentido] = leer_excel_a_json(path)

# -------------------------------
# LISTAR ESTACIONES
# -------------------------------
def listar_estaciones():
    estaciones_set = set()
    for dia, sentidos in DATOS.items():
        for sentido, horarios in sentidos.items():
            for fila in horarios:
                estaciones_set.update(fila.keys())
    return sorted(estaciones_set)

# -------------------------------
# APP FASTAPI
# -------------------------------
app = FastAPI(title="Horarios de Tren", version="5.0")

@app.get("/tren")
def get_tren(
    dia: str = Query(...),
    sentido: str = Query(...),
    origen: str = Query(None),
    destino: str = Query(None)
):
    dia = dia.lower()
    sentido = sentido.lower()
    if dia not in DATOS or sentido not in DATOS[dia]:
        return JSONResponse({"error": "Parámetros inválidos"}, status_code=400)
    horarios = DATOS[dia][sentido]
    if origen and destino:
        filtrados = []
        for fila in horarios:
            if origen in fila and destino in fila:
                filtrados.append({
                    "origen": origen,
                    "hora_origen": fila[origen],
                    "destino": destino,
                    "hora_destino": fila[destino]
                })
        return JSONResponse({"tren": "Lunes a Viernes" if dia=="lv" else "Sábado y Domingo",
                             "sentido": sentido.capitalize(),
                             "horarios_filtrados": filtrados})
    return JSONResponse({"tren": "Lunes a Viernes" if dia=="lv" else "Sábado y Domingo",
                         "sentido": sentido.capitalize(),
                         "horarios": horarios})

@app.get("/tren/estaciones")
def get_estaciones():
    return JSONResponse({"estaciones": listar_estaciones()})

@app.get("/tren/proximo")
def get_proximo_tren(
    dia: str = Query(...),
    sentido: str = Query(...),
    origen: str = Query(...),
    destino: str = Query(...),
    hora: str = Query(None)
):
    dia = dia.lower()
    sentido = sentido.lower()
    if dia not in DATOS or sentido not in DATOS[dia]:
        return JSONResponse({"error": "Parámetros inválidos"}, status_code=400)

    horarios = DATOS[dia][sentido]
    hora_minima = datetime.now().time() if not hora else datetime.strptime(hora, "%H:%M").time()

    for fila in horarios:
        if origen in fila and destino in fila:
            try:
                hora_origen = datetime.strptime(fila[origen], "%H:%M").time()
            except:
                continue
            if hora_origen >= hora_minima:
                return JSONResponse({
                    "tren": "Lunes a Viernes" if dia=="lv" else "Sábado y Domingo",
                    "sentido": sentido.capitalize(),
                    "proximo_tren": {
                        "origen": origen,
                        "hora_origen": fila[origen],
                        "destino": destino,
                        "hora_destino": fila[destino]
                    }
                })
    return JSONResponse({"mensaje": "No hay trenes disponibles a partir de la hora indicada"})

# -------------------------------
# TEST LOCAL
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
