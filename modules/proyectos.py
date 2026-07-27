import streamlit as st
import pandas as pd
import uuid
import datetime
from utils.helpers import cargar_json, guardar_json

# Constantes de archivos JSON
PROYECTOS_FILE = "proyectos.json"
CLIENTES_FILE = "clientes.json"

# Opciones fijas para el estado del proyecto
ESTADOS_PROYECTO = ["Pendiente", "En progreso", "Completado"]

def render_modulo_proyectos():
    """
    Renderiza la interfaz de usuario para la Gestión de Proyectos en Streamlit.
    Incluye buscador rápido, métricas de resumen, tabla con badges estilizados, 
    y flujo completo CRUD (Crear, Leer, Editar, Eliminar) con soporte de presupuesto.
    """
    st.title("📁 Gestión de Proyectos")
    st.caption("Administra los proyectos de desarrollo de **SoftDev** y realiza seguimiento a su estado.")
    st.divider()

    # Cargar datos actuales
    proyectos = cargar_json(PROYECTOS_FILE)
    clientes = cargar_json(CLIENTES_FILE)

    # Creamos pestañas para organizar el flujo de trabajo
    tab_listar, tab_crear, tab_editar, tab_eliminar = st.tabs([
        "📋 Listado y Filtros", 
        "➕ Nuevo Proyecto", 
        "✏️ Editar", 
        "🗑️ Eliminar"
    ])

    # -------------------------------------------------------------------------
    # PESTAÑA 1: LISTAR PROYECTOS (Buscador, KPIs, Filtro y Tabla con Badges)
    # -------------------------------------------------------------------------
    with tab_listar:
        st.subheader("Listado de Proyectos Registrados")

        # Mapeo rápido de ID de cliente a Nombre de Empresa
        mapa_clientes = {c["id"]: c.get("empresa", c.get("nombre", "Desconocido")) for c in clientes}

        # --- SECCIÓN DE MÉTRICAS RÁPIDAS (KPIs) ---
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        total_p = len(proyectos)
        completados = sum(1 for p in proyectos if p.get("estado") == "Completado")
        en_progreso = sum(1 for p in proyectos if p.get("estado") == "En progreso")
        presupuesto_total = sum(float(p.get("presupuesto", 0)) for p in proyectos)

        col_kpi1.metric("Total Proyectos", total_p)
        col_kpi2.metric("En Progreso", en_progreso)
        col_kpi3.metric("Completados", completados)
        col_kpi4.metric("Presupuesto Total", f"${presupuesto_total:,.2f}")

        st.write("") # Espaciador

        # --- CONTROLES DE BÚSQUEDA Y FILTRADO ---
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            busqueda = st.text_input("🔍 Buscar por nombre de proyecto:", "", key="search_proyecto")
        with col_filter:
            filtro_estado = st.selectbox(
                "Filtrar por Estado:", 
                ["Todos"] + ESTADOS_PROYECTO,
                key="filtro_estado_proyectos"
            )

        # Aplicar filtros
        proyectos_filtrados = proyectos
        
        # Filtro por texto
        if busqueda:
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if busqueda.lower() in p.get("nombre", "").lower()
            ]
        
        # Filtro por estado
        if filtro_estado != "Todos":
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if p.get("estado") == filtro_estado
            ]

        # --- CONSTRUCCIÓN DE LA TABLA CON BADGES ---
        if not proyectos_filtrados:
            st.info("No se encontraron proyectos que coincidan con la búsqueda o filtro seleccionado.")
        else:
            proyectos_display = []
            for p in proyectos_filtrados:
                estado = p.get("estado", "Pendiente")
                
                # Asignación de Badge según estado
                if estado == "Completado":
                    estado_badge = "🟢 Completado"
                elif estado == "En progreso":
                    estado_badge = "🔵 En progreso"
                else:
                    estado_badge = "🟡 Pendiente"

                nombre_cliente = mapa_clientes.get(p.get("cliente_id"), p.get("cliente", "Cliente no encontrado"))

                proyectos_display.append({
                    "Código": p.get("id", "-"),
                    "Nombre del Proyecto": p.get("nombre", "-"),
                    "Cliente": nombre_cliente,
                    "Fecha Inicio": p.get("fecha_inicio", "-"),
                    "Fecha Entrega": p.get("fecha_entrega", "-"),
                    "Estado": estado_badge,
                    "Presupuesto ($)": f"${float(p.get('presupuesto', 0)):,.2f}"
                })

            df_proyectos = pd.DataFrame(proyectos_display)
            st.dataframe(
                df_proyectos,
                use_container_width=True,
                hide_index=True
            )

    # -------------------------------------------------------------------------
    # PESTAÑA 2: REGISTRAR NUEVO PROYECTO
    # -------------------------------------------------------------------------
    with tab_crear:
        st.subheader("Registrar Nuevo Proyecto")
        
        if not clientes:
            st.warning("⚠️ Debes registrar al menos un **Cliente** antes de poder crear un proyecto.")
        else:
            opciones_clientes = {f"{c.get('empresa', 'Sin Empresa')} ({c.get('nombre', 'Sin Nombre')})": c["id"] for c in clientes}

            with st.form("form_nuevo_proyecto", clear_on_submit=True):
                nombre_proyecto = st.text_input("Nombre del Proyecto*")
                cliente_seleccionado_str = st.selectbox("Cliente Asignado*", list(opciones_clientes.keys()))
                
                col1, col2 = st.columns(2)
                with col1:
                    fecha_inicio = st.date_input("Fecha de Inicio", datetime.date.today())
                with col2:
                    fecha_entrega = st.date_input("Fecha de Entrega Estimada", datetime.date.today() + datetime.timedelta(days=30))
                
                col3, col4 = st.columns(2)
                with col3:
                    estado_inicial = st.selectbox("Estado Inicial", ESTADOS_PROYECTO, index=0)
                with col4:
                    presupuesto = st.number_input("Presupuesto ($)", min_value=0.0, step=100.0, value=1000.0)

                submit = st.form_submit_button("Guardar Proyecto")

                if submit:
                    if not nombre_proyecto.strip():
                        st.error("El nombre del proyecto es obligatorio.")
                    elif fecha_entrega < fecha_inicio:
                        st.error("La fecha de entrega no puede ser anterior a la fecha de inicio.")
                    else:
                        cliente_id = opciones_clientes[cliente_seleccionado_str]
                        
                        nuevo_proyecto = {
                            "id": str(uuid.uuid4())[:8],
                            "nombre": nombre_proyecto.strip(),
                            "cliente_id": cliente_id,
                            "fecha_inicio": str(fecha_inicio),
                            "fecha_entrega": str(fecha_entrega),
                            "estado": estado_inicial,
                            "presupuesto": presupuesto
                        }
                        
                        proyectos.append(nuevo_proyecto)
                        guardar_json(PROYECTOS_FILE, proyectos)
                        st.success(f"Proyecto '{nombre_proyecto}' registrado correctamente.")
                        st.rerun()

    # -------------------------------------------------------------------------
    # PESTAÑA 3: EDITAR PROYECTO
    # -------------------------------------------------------------------------
    with tab_editar:
        st.subheader("Editar Proyecto Existente")
        
        if not proyectos:
            st.info("No hay proyectos registrados para editar.")
        else:
            opciones_proyectos = {
                f"{p['nombre']} [{mapa_clientes.get(p.get('cliente_id'), 'Sin Cliente')}]": p 
                for p in proyectos
            }
            
            p_key = st.selectbox("Selecciona un proyecto:", list(opciones_proyectos.keys()), key="select_edit_p")
            p_sel = opciones_proyectos[p_key]

            opciones_clientes = {f"{c.get('empresa', 'Sin Empresa')} ({c.get('nombre', 'Sin Nombre')})": c["id"] for c in clientes}
            
            # Mapeo de índices por defecto
            idx_cliente_actual = 0
            for i, (k, v) in enumerate(opciones_clientes.items()):
                if v == p_sel.get("cliente_id"):
                    idx_cliente_actual = i
                    break

            idx_estado_actual = ESTADOS_PROYECTO.index(p_sel["estado"]) if p_sel.get("estado") in ESTADOS_PROYECTO else 0

            # Conversión de fechas
            f_inicio_val = datetime.datetime.strptime(p_sel["fecha_inicio"], "%Y-%m-%d").date() if p_sel.get("fecha_inicio") else datetime.date.today()
            f_entrega_val = datetime.datetime.strptime(p_sel["fecha_entrega"], "%Y-%m-%d").date() if p_sel.get("fecha_entrega") else datetime.date.today()

            with st.form("form_editar_proyecto"):
                nuevo_nombre_p = st.text_input("Nombre del Proyecto", value=p_sel.get("nombre", ""))
                nuevo_cliente_str = st.selectbox("Cliente Asignado", list(opciones_clientes.keys()), index=idx_cliente_actual)
                
                col1, col2 = st.columns(2)
                with col1:
                    nueva_f_inicio = st.date_input("Fecha de Inicio", value=f_inicio_val)
                with col2:
                    nueva_f_entrega = st.date_input("Fecha de Entrega", value=f_entrega_val)

                col3, col4 = st.columns(2)
                with col3:
                    nuevo_estado = st.selectbox("Estado", ESTADOS_PROYECTO, index=idx_estado_actual)
                with col4:
                    nuevo_presupuesto = st.number_input("Presupuesto ($)", min_value=0.0, step=100.0, value=float(p_sel.get("presupuesto", 0.0)))

                btn_actualizar_p = st.form_submit_button("Actualizar Proyecto")

                if btn_actualizar_p:
                    if not nuevo_nombre_p.strip():
                        st.error("El nombre del proyecto no puede estar vacío.")
                    elif nueva_f_entrega < nueva_f_inicio:
                        st.error("La fecha de entrega no puede ser anterior a la fecha de inicio.")
                    else:
                        p_sel["nombre"] = nuevo_nombre_p.strip()
                        p_sel["cliente_id"] = opciones_clientes[nuevo_cliente_str]
                        p_sel["fecha_inicio"] = str(nueva_f_inicio)
                        p_sel["fecha_entrega"] = str(nueva_f_entrega)
                        p_sel["estado"] = nuevo_estado
                        p_sel["presupuesto"] = nuevo_presupuesto

                        guardar_json(PROYECTOS_FILE, proyectos)
                        st.success("Proyecto actualizado correctamente.")
                        st.rerun()

    # -------------------------------------------------------------------------
    # PESTAÑA 4: ELIMINAR PROYECTO
    # -------------------------------------------------------------------------
    with tab_eliminar:
        st.subheader("Eliminar Proyecto")
        
        if not proyectos:
            st.info("No hay proyectos para eliminar.")
        else:
            opciones_del_p = {
                f"{p['nombre']} [{mapa_clientes.get(p.get('cliente_id'), 'Sin Cliente')}]": p 
                for p in proyectos
            }
            
            p_del_key = st.selectbox("Selecciona el proyecto a eliminar:", list(opciones_del_p.keys()), key="select_del_p")
            p_del = opciones_del_p[p_del_key]

            st.warning(f"⚠️ ¿Estás seguro de eliminar el proyecto **'{p_del['nombre']}'**?")
            
            if st.button("Confirmar Eliminación", type="primary", key="btn_confirm_del_p"):
                proyectos_actualizados = [p for p in proyectos if p["id"] != p_del["id"]]
                guardar_json(PROYECTOS_FILE, proyectos_actualizados)
                st.success(f"Proyecto '{p_del['nombre']}' eliminado con éxito.")
                st.rerun()