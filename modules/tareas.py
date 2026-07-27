import streamlit as st
import pandas as pd
import uuid
from utils.helpers import cargar_json, guardar_json

# Constantes de archivos JSON
TAREAS_FILE = "tareas.json"
PROYECTOS_FILE = "proyectos.json"

# Opciones fijas para prioridades y estados de tareas
PRIORIDADES_TAREA = ["Baja", "Media", "Alta"]
ESTADOS_TAREA = ["Pendiente", "En progreso", "Completada"]

def render_modulo_tareas():
    """
    Renderiza la interfaz de usuario para la Gestión de Tareas en Streamlit.
    Permite visualizar tareas mediante un buscador global con Badges o interactivamente por proyecto,
    asignar nuevas tareas a proyectos existentes y eliminarlas.
    """
    st.title("✅ Gestión de Tareas")
    st.caption("Asignación, seguimiento y organización de tareas en **SoftDev**.")
    st.divider()

    # Cargar datos actuales
    tareas = cargar_json(TAREAS_FILE)
    proyectos = cargar_json(PROYECTOS_FILE)

    # Mapeo rápido de ID de Proyecto a Nombre de Proyecto
    mapa_proyectos = {p["id"]: p.get("nombre", "Sin Proyecto") for p in proyectos}

    # Definición de pestañas para organizar el módulo
    tab_interactivo, tab_tabla_general, tab_crear, tab_eliminar = st.tabs([
        "⚡ Gestión Interactiva",
        "📌 Vista General (Tabla)",
        "➕ Nueva Tarea",
        "🗑️ Eliminar Tarea"
    ])

    # -------------------------------------------------------------------------
    # PESTAÑA 1: GESTIÓN INTERACTIVA POR PROYECTO (Cambio rápido de estado)
    # -------------------------------------------------------------------------
    with tab_interactivo:
        st.subheader("Seguimiento Interactivo por Proyecto")

        if not proyectos:
            st.info("No hay proyectos registrados. Crea un proyecto primero para asociarle tareas.")
        else:
            # Selector de Proyecto para trabajar de manera enfocada
            opciones_proyectos = {p["nombre"]: p["id"] for p in proyectos}
            nombre_p_sel = st.selectbox("Selecciona un Proyecto para gestionar sus tareas:", list(opciones_proyectos.keys()), key="select_p_interactivo")
            id_p_sel = opciones_proyectos[nombre_p_sel]

            # Filtrar tareas del proyecto seleccionado
            tareas_proyecto = [t for t in tareas if t.get("proyecto_id") == id_p_sel]

            if not tareas_proyecto:
                st.info(f"El proyecto **'{nombre_p_sel}'** aún no tiene tareas asignadas.")
            else:
                st.markdown(f"### Tareas de: *{nombre_p_sel}*")

                hubo_cambios = False
                for t in tareas_proyecto:
                    col_info, col_estado, col_accion = st.columns([3, 2, 2])

                    # Soporte flexible para claves 'titulo' o 'descripcion'
                    titulo_tarea = t.get("titulo") or t.get("descripcion", "Sin título")

                    with col_info:
                        prioridad = t.get("prioridad", "Media")
                        color_prio = "🔴" if prioridad == "Alta" else ("🟡" if prioridad == "Media" else "🟢")
                        st.markdown(f"**{titulo_tarea}**")
                        st.caption(f"👤 Responsable: {t.get('responsable', 'Sin asignar')} | Prioridad: {color_prio} {prioridad}")

                    with col_estado:
                        # Selector para cambiar el estado dinámicamente
                        estado_actual = t.get("estado", "Pendiente")
                        idx_est = ESTADOS_TAREA.index(estado_actual) if estado_actual in ESTADOS_TAREA else 0
                        nuevo_est = st.selectbox(
                            "Estado", 
                            ESTADOS_TAREA, 
                            index=idx_est,
                            key=f"estado_t_{t['id']}"
                        )
                        if nuevo_est != estado_actual:
                            t["estado"] = nuevo_est
                            hubo_cambios = True

                    with col_accion:
                        # Casilla de verificación rápida para marcar como Completada
                        es_completada = (t.get("estado") == "Completada")
                        marcado = st.checkbox("✔ Completada", value=es_completada, key=f"chk_comp_{t['id']}")
                        
                        if marcado and t.get("estado") != "Completada":
                            t["estado"] = "Completada"
                            hubo_cambios = True
                        elif not marcado and t.get("estado") == "Completada":
                            t["estado"] = "Pendiente"
                            hubo_cambios = True

                    st.divider()

                if hubo_cambios:
                    guardar_json(TAREAS_FILE, tareas)
                    st.toast("¡Estado de tarea actualizado con éxito!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # PESTAÑA 2: VISTA GENERAL EN TABLA CON BUSCADOR Y BADGES
    # -------------------------------------------------------------------------
    with tab_tabla_general:
        st.subheader("📌 Tareas en Sistema")

        # --- KPIs RÁPIDOS ---
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        total_t = len(tareas)
        comp_t = sum(1 for t in tareas if t.get("estado") == "Completada")
        pend_t = total_t - comp_t

        col_kpi1.metric("Total Tareas", total_t)
        col_kpi2.metric("Completadas", comp_t)
        col_kpi3.metric("Pendientes / En Progreso", pend_t)

        st.write("")

        # --- BUSCADOR RÁPIDO ---
        busqueda = st.text_input("🔍 Buscar tarea por título/descripción o responsable:", "", key="search_tarea")

        if busqueda:
            tareas_filtradas = [
                t for t in tareas 
                if busqueda.lower() in (t.get("titulo") or t.get("descripcion", "")).lower() 
                or busqueda.lower() in t.get("responsable", "").lower()
            ]
        else:
            tareas_filtradas = tareas

        if not tareas_filtradas:
            st.info("No hay tareas registradas que coincidan con la búsqueda.")
        else:
            tareas_display = []
            for t in tareas_filtradas:
                prioridad = t.get("prioridad", "Media")
                estado = t.get("estado", "Pendiente")

                # Badges para Prioridad
                if prioridad == "Alta":
                    p_badge = "🔴 Alta"
                elif prioridad == "Media":
                    p_badge = "🟡 Media"
                else:
                    p_badge = "🟢 Baja"

                # Badges para Estado
                if estado == "Completada":
                    e_badge = "🟢 Completada"
                elif estado == "En progreso":
                    e_badge = "🔵 En progreso"
                else:
                    e_badge = "⏳ Pendiente"

                nombre_proyecto = mapa_proyectos.get(t.get("proyecto_id"), "Sin Proyecto")
                titulo_o_desc = t.get("titulo") or t.get("descripcion", "-")

                tareas_display.append({
                    "ID": t.get("id", "-"),
                    "Tarea": titulo_o_desc,
                    "Proyecto": nombre_proyecto,
                    "Responsable": t.get("responsable", "-"),
                    "Prioridad": p_badge,
                    "Estado": e_badge
                })

            df_tareas = pd.DataFrame(tareas_display)
            st.dataframe(
                df_tareas,
                use_container_width=True,
                hide_index=True
            )

    # -------------------------------------------------------------------------
    # PESTAÑA 3: REGISTRAR NUEVA TAREA
    # -------------------------------------------------------------------------
    with tab_crear:
        st.subheader("Registrar Nueva Tarea")

        if not proyectos:
            st.warning("⚠️ Debes registrar al menos un **Proyecto** antes de poder agregar tareas.")
        else:
            opciones_proyectos_crear = {p["nombre"]: p["id"] for p in proyectos}

            with st.form("form_nueva_tarea", clear_on_submit=True):
                proyecto_asig = st.selectbox("Proyecto Asociado*", list(opciones_proyectos_crear.keys()))
                titulo = st.text_input("Título / Nombre Corto de la Tarea*")
                descripcion = st.text_area("Descripción detallada (Opcional)")
                
                col1, col2 = st.columns(2)
                with col1:
                    responsable = st.text_input("Responsable / Desarrollador*")
                with col2:
                    prioridad = st.selectbox("Prioridad", PRIORIDADES_TAREA, index=1) # Por defecto Media

                submit = st.form_submit_button("Guardar Tarea")

                if submit:
                    if not titulo.strip() or not responsable.strip():
                        st.error("Los campos 'Título' y 'Responsable' son obligatorios.")
                    else:
                        nueva_tarea = {
                            "id": str(uuid.uuid4())[:8],
                            "proyecto_id": opciones_proyectos_crear[proyecto_asig],
                            "titulo": titulo.strip(),
                            "descripcion": descripcion.strip(),
                            "responsable": responsable.strip(),
                            "prioridad": prioridad,
                            "estado": "Pendiente"
                        }

                        tareas.append(nueva_tarea)
                        guardar_json(TAREAS_FILE, tareas)
                        st.success("Tarea asignada con éxito.")
                        st.rerun()

    # -------------------------------------------------------------------------
    # PESTAÑA 4: ELIMINAR TAREA
    # -------------------------------------------------------------------------
    with tab_eliminar:
        st.subheader("Eliminar Tarea")

        if not tareas:
            st.info("No hay tareas registradas para eliminar.")
        else:
            opciones_del_t = {}
            for t in tareas:
                nombre_p = mapa_proyectos.get(t.get("proyecto_id"), "Sin Proyecto")
                texto_t = t.get("titulo") or t.get("descripcion", "Sin nombre")
                label = f"[{nombre_p}] - {texto_t[:35]}... ({t.get('responsable', 'Sin asignado')})"
                opciones_del_t[label] = t

            t_del_key = st.selectbox("Selecciona la tarea a eliminar:", list(opciones_del_t.keys()), key="select_del_t")
            t_del = opciones_del_t[t_del_key]

            texto_confirmacion = t_del.get("titulo") or t_del.get("descripcion", "")
            st.warning(f"⚠️ ¿Estás seguro de eliminar la tarea **'{texto_confirmacion}'**?")

            if st.button("Confirmar Eliminación", type="primary", key="btn_confirm_del_t"):
                tareas_actualizadas = [t for t in tareas if t["id"] != t_del["id"]]
                guardar_json(TAREAS_FILE, tareas_actualizadas)
                st.success("Tarea eliminada correctamente.")
                st.rerun()