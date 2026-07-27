import streamlit as st
import pandas as pd
import io
from utils.helpers import cargar_json
from modules.clientes import render_modulo_clientes
from modules.proyectos import render_modulo_proyectos
from modules.tareas import render_modulo_tareas
from modules.ia import render_modulo_ia

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SoftDev — Sistema de Gestión Interna",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nombres de archivos JSON
CLIENTES_FILE = "clientes.json"
PROYECTOS_FILE = "proyectos.json"
TAREAS_FILE = "tareas.json"

# -----------------------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS
# -----------------------------------------------------------------------------
def aplicar_estilos_css():
    st.markdown("""
        <style>
        .kpi-card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease-in-out;
        }
        .kpi-card:hover {
            transform: translateY(-3px);
            border-color: #3b82f6;
        }
        .kpi-icon {
            font-size: 26px;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: #f8fafc;
        }
        .kpi-label {
            font-size: 13px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .hero-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border: 1px solid #3b82f640;
            border-left: 6px solid #3b82f6;
            padding: 20px 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)


def generar_excel(df):
    """Convierte un DataFrame a un buffer binario de Excel (.xlsx)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()


def render_dashboard():
    """Renderiza la vista principal con métricas, filtros y descargas."""
    
    # BANNER INSTITUCIONAL
    st.markdown(
        """
        <div class="hero-banner">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; font-size: 18px; color: #60a5fa;">
                        🎓 Universidad Privada Domingo Savio
                    </h4>
                    <p style="margin: 6px 0 0 0; font-size: 14px; color: #cbd5e1;">
                        <b>Materia:</b> Hardware, Software y Redes &nbsp;|&nbsp; 
                        <b>Equipo:</b> Estudiantes de 1.º Semestre
                    </p>
                </div>
                <div style="text-align: right; background-color: #334155; padding: 6px 14px; border-radius: 20px;">
                    <span style="color: #4ade80; font-size: 13px;">🟢 Sistema Activo (LAN)</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.title("⚡ Dashboard de Control")
    st.caption("Resumen general y métricas en tiempo real de la empresa **SoftDev**.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Cargar datos desde JSON
    clientes = cargar_json(CLIENTES_FILE)
    proyectos = cargar_json(PROYECTOS_FILE)
    tareas = cargar_json(TAREAS_FILE)

    # -------------------------------------------------------------------------
    # FILTRO DINÁMICO (Mejora 2)
    # -------------------------------------------------------------------------
    col_filtro, _ = st.columns([2, 2])
    with col_filtro:
        filtro_estado = st.selectbox(
            "🔍 Filtrar Proyectos por Estado:",
            ["Todos", "Pendiente", "En progreso", "Completado"]
        )

    # Aplicar filtro
    proyectos_filtrados = proyectos if filtro_estado == "Todos" else [p for p in proyectos if p.get("estado") == filtro_estado]

    # -------------------------------------------------------------------------
    # CÁLCULO DE MÉTRICAS
    # -------------------------------------------------------------------------
    total_clientes = len(clientes)
    proyectos_activos = sum(1 for p in proyectos_filtrados if p.get("estado") in ["Pendiente", "En progreso"])
    proyectos_completados = sum(1 for p in proyectos_filtrados if p.get("estado") == "Completado")
    tareas_pendientes = sum(1 for t in tareas if t.get("estado") != "Completada")

    # -------------------------------------------------------------------------
    # TARJETAS KPIs
    # -------------------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">👥</div>
                <div class="kpi-value">{total_clientes}</div>
                <div class="kpi-label">Clientes Registrados</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🚀</div>
                <div class="kpi-value">{proyectos_activos}</div>
                <div class="kpi-label">Proyectos Activos</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">✅</div>
                <div class="kpi-value">{proyectos_completados}</div>
                <div class="kpi-label">Proyectos Completados</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">📌</div>
                <div class="kpi-value">{tareas_pendientes}</div>
                <div class="kpi-label">Tareas Pendientes</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # PESTAÑAS Y EXPORTACIÓN A EXCEL (Mejora 3)
    # -------------------------------------------------------------------------
    tab_grafico, tab_reportes, tab_alertas = st.tabs([
        "📊 Distribución de Proyectos", 
        "📥 Reportes Excel", 
        "🔔 Notificaciones y Alertas"
    ])

    with tab_grafico:
        if not proyectos_filtrados:
            st.info("No hay proyectos para mostrar con el filtro seleccionado.")
        else:
            estados_count = {
                "Pendiente": sum(1 for p in proyectos_filtrados if p.get("estado") == "Pendiente"),
                "En progreso": sum(1 for p in proyectos_filtrados if p.get("estado") == "En progreso"),
                "Completado": sum(1 for p in proyectos_filtrados if p.get("estado") == "Completado")
            }
            df_estados = pd.DataFrame(list(estados_count.items()), columns=["Estado", "Cantidad"]).set_index("Estado")
            st.bar_chart(df_estados)

    with tab_reportes:
        st.markdown("### 📊 Descarga de Reportes Ejecutivos")
        st.caption("Genera archivos en formato Excel para la gestión de la empresa.")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            st.markdown("#### 📁 Reporte de Proyectos")
            if proyectos:
                df_proyectos = pd.DataFrame(proyectos)
                excel_proyectos = generar_excel(df_proyectos)
                st.download_button(
                    label="📊 Descargar Proyectos (.xlsx)",
                    data=excel_proyectos,
                    file_name="Reporte_Proyectos_SoftDev.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.caption("No hay datos de proyectos.")

        with col_exp2:
            st.markdown("#### 👥 Reporte de Clientes")
            if clientes:
                df_clientes = pd.DataFrame(clientes)
                excel_clientes = generar_excel(df_clientes)
                st.download_button(
                    label="📊 Descargar Clientes (.xlsx)",
                    data=excel_clientes,
                    file_name="Reporte_Clientes_SoftDev.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.caption("No hay datos de clientes.")

    with tab_alertas:
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.markdown("### 📋 Totales Operativos")
            st.markdown(f"- **Proyectos en Sistema:** `{len(proyectos)}`")
            st.markdown(f"- **Tareas Registradas:** `{len(tareas)}`")
        
        with col_a2:
            st.markdown("### ⚠️ Estado de Prioridades")
            tareas_criticas = [t for t in tareas if t.get("prioridad") == "Alta" and t.get("estado") != "Completada"]
            if tareas_criticas:
                st.warning(f"Hay **{len(tareas_criticas)} tarea(s) de alta prioridad** pendientes.")
            else:
                st.success("🎉 ¡Excelente! No hay tareas críticas pendientes.")


def main():
    aplicar_estilos_css()

    # -------------------------------------------------------------------------
    # MENÚ LATERAL (SIDEBAR) CON MONITOR DE RED (Mejora 1)
    # -------------------------------------------------------------------------
    st.sidebar.title("💻 SoftDev ERP")
    st.sidebar.caption("Panel Administrativo Interno")
    st.sidebar.markdown("---")

    opcion = st.sidebar.radio(
        "Módulos del Sistema:",
        ["🏠 Inicio", "👥 Clientes", "📁 Proyectos", "✅ Tareas", "🤖 Asistente IA"]
    )

    st.sidebar.markdown("---")
    
    # MONITOR DE RED LOCAL
    st.sidebar.markdown("### 🌐 Servidor y Red LAN")
    st.sidebar.code("Host: 192.168.1.15\nPort: 8501\nProtocolo: HTTP/TCP")
    st.sidebar.caption("Servidor local activo — UPDS Network")

    st.sidebar.markdown("---")
    st.sidebar.caption("SoftDev © 2026 — UPDS")

    # Renderizado condicional
    if opcion == "🏠 Inicio":
        render_dashboard()
    elif opcion == "👥 Clientes":
        render_modulo_clientes()
    elif opcion == "📁 Proyectos":
        render_modulo_proyectos()
    elif opcion == "✅ Tareas":
        render_modulo_tareas()
    elif opcion == "🤖 Asistente IA":
        render_modulo_ia()


if __name__ == "__main__":
    main()