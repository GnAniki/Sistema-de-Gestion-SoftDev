import streamlit as st
import urllib.request
import json
import datetime
from utils.helpers import cargar_json

# Constantes de configuración de Ollama y archivos de datos
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"  # Nombre del modelo en Ollama (Phi-3 Mini)

CLIENTES_FILE = "clientes.json"
PROYECTOS_FILE = "proyectos.json"
TAREAS_FILE = "tareas.json"


def consultar_ollama(prompt: str) -> str:
    """
    Envía una petición HTTP POST al endpoint local de Ollama utilizando la librería 
    estándar urllib.request (sin depender de paquetes de terceros como 'requests').
    Retorna el texto generado por el modelo local.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False  # Obtenemos la respuesta completa en una sola llamada
    }
    
    # Convertimos la carga útil a JSON codificado en bytes
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status == 200:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "No se recibió respuesta válida del modelo.")
            else:
                return f"Error HTTP {response.status}: No se pudo comunicar con Ollama."
    except urllib.error.URLError as e:
        return (
            f"❌ No se pudo conectar con Ollama en '{OLLAMA_URL}'. "
            "Asegúrate de que Ollama esté corriendo localmente en tu sistema "
            f"y que tengas el modelo instalado (ej: 'ollama run {MODEL_NAME}'). Detalle: {e}"
        )
    except Exception as e:
        return f"Ocurrió un error inesperado al consultar la IA: {e}"


def construir_prompt_reporte(clientes: list, proyectos: list, tareas: list) -> str:
    """
    Formatea la información estructurada de los JSON en un prompt claro
    y en español para que Ollama Phi-3 analice el estado actual de SoftDev.
    """
    hoy = datetime.date.today()
    mapa_clientes = {c["id"]: c["empresa"] for c in clientes}

    # Resumen de proyectos
    resumen_proyectos = []
    for p in proyectos:
        cliente_nombre = mapa_clientes.get(p.get("cliente_id"), "Desconocido")
        # Identificar si está atrasado
        f_entrega = p.get("fecha_entrega")
        es_atrasado = False
        if f_entrega and p.get("estado") != "Completado":
            try:
                f_obj = datetime.datetime.strptime(f_entrega, "%Y-%m-%d").date()
                if f_obj < hoy:
                    es_atrasado = True
            except ValueError:
                pass

        estado_str = f"{p.get('estado')}" + (" [⚠️ ATRASADO]" if es_atrasado else "")
        resumen_proyectos.append(
            f"- Proyecto: '{p.get('nombre')}' | Cliente: {cliente_nombre} | "
            f"Fecha Entrega: {f_entrega} | Estado: {estado_str}"
        )

    # Resumen de tareas
    resumen_tareas = []
    for t in tareas:
        resumen_tareas.append(
            f"- Tarea: '{t.get('descripcion')}' | Responsable: {t.get('responsable')} | "
            f"Prioridad: {t.get('prioridad')} | Estado: {t.get('estado')}"
        )

    str_proyectos = "\n".join(resumen_proyectos) if resumen_proyectos else "No hay proyectos registrados."
    str_tareas = "\n".join(resumen_tareas) if resumen_tareas else "No hay tareas registradas."

    prompt = f"""
Eres un Asistente Senior de Gestión de Proyectos en la empresa de software 'SoftDev'.
Analiza la siguiente información actual de la empresa (Fecha de hoy: {hoy}):

--- DATOS DE PROYECTOS ---
{str_proyectos}

--- DATOS DE TAREAS ---
{str_tareas}

INSTRUCCIONES:
1. Genera un reporte ejecutivo breve en español (máximo 3 párrafos).
2. Menciona la cantidad total de proyectos activos y resalta si alguno está atrasado o crítico.
3. Analiza las tareas pendientes y da una recomendación clara sobre qué área o responsable debe priorizar trabajo.
4. Mantén un tono profesional, directo y estructurado.
"""
    return prompt


def render_modulo_ia():
    """
    Renderiza la interfaz para interactuar con Ollama Phi-3 Mini y generar reportes automáticos.
    """
    st.title("🤖 Asistente IA (Ollama — Phi-3 Mini)")
    st.markdown("Generación de reportes ejecutivos automatizados del estado operativo de SoftDev mediante IA local.")
    st.divider()

    # Cargar datos
    clientes = cargar_json(CLIENTES_FILE)
    proyectos = cargar_json(PROYECTOS_FILE)
    tareas = cargar_json(TAREAS_FILE)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Generador de Reporte Automático")
        st.markdown(
            "Al hacer clic en el botón, la IA analizará los datos de **clientes, proyectos y tareas** "
            "almacenados en los archivos JSON y redactará un diagnóstico en tiempo real sin salir de tu red local."
        )

    with col2:
        st.info(f"**Servidor local:** `{OLLAMA_URL}`\n\n**Modelo:** `{MODEL_NAME}`")

    st.divider()

    # Botón principal para activar la IA
    if st.button("🚀 Generar Reporte de Estado", type="primary", use_container_width=True):
        if not proyectos and not tareas:
            st.warning("⚠️ No hay suficientes datos de proyectos o tareas para generar un reporte significativo.")
        else:
            with st.spinner("🤖 La IA está analizando los datos y redactando el informe... Por favor espera unos segundos."):
                # 1. Construir prompt contextual
                prompt = construir_prompt_reporte(clientes, proyectos, tareas)
                
                # 2. Consultar servidor local Ollama
                respuesta_ia = consultar_ollama(prompt)

            st.success("✨ Reporte generado con éxito:")
            st.markdown(f"> {respuesta_ia}")

            # Expandible técnico para auditar el prompt enviado
            with st.expander("🔍 Ver prompt enviado a la IA (Auditoría de datos)"):
                st.code(prompt, language="text")