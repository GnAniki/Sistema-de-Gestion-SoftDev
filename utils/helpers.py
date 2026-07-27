import json
import os
from typing import List, Dict, Any

# Definición de rutas base para mantener centralizada la configuración de archivos
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def obtener_ruta_json(nombre_archivo: str) -> str:
    """Retorna la ruta absoluta de un archivo JSON dentro de la carpeta data/."""
    return os.path.join(DATA_DIR, nombre_archivo)

def cargar_json(nombre_archivo: str) -> List[Dict[str, Any]]:
    """
    Lee un archivo JSON y retorna su contenido como lista de diccionarios.
    Si el archivo no existe o está corrupto, lo inicializa de forma segura con una lista vacía.
    """
    ruta = obtener_ruta_json(nombre_archivo)
    
    # Asegurar que el directorio data/ exista
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(ruta):
        guardar_json(nombre_archivo, [])
        return []
    
    try:
        with open(ruta, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        # Si ocurre un error al leer, retornamos una lista vacía para evitar crash
        return []

def guardar_json(nombre_archivo: str, datos: List[Dict[str, Any]]) -> None:
    """
    Guarda una lista de diccionarios en el archivo JSON especificado dentro de data/.
    Aplica indentación para mantener los archivos legibles.
    """
    ruta = obtener_ruta_json(nombre_archivo)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(ruta, "w", encoding="utf-8") as file:
        json.dump(datos, file, ensure_ascii=False, indent=4)