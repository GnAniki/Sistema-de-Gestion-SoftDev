import streamlit as st
import pandas as pd
import uuid
from utils.helpers import cargar_json, guardar_json

# Constante para el nombre del archivo JSON
CLIENTES_FILE = "clientes.json"

def render_modulo_clientes():
    """
    Renderiza la interfaz de usuario para la Gestión de Clientes en Streamlit.
    Proporciona funcionalidades CRUD completas (Crear, Leer, Editar, Eliminar)
    junto con buscador dinámico en tiempo real y vista en tabla optimizada con Pandas.
    """
    st.title("👥 Gestión de Clientes")
    st.caption("Directorio de clientes y organizaciones de la empresa **SoftDev**.")
    st.divider()

    # Cargar datos actuales
    clientes = cargar_json(CLIENTES_FILE)

    # Creamos pestañas para organizar la interfaz
    tab_listar, tab_crear, tab_editar, tab_eliminar = st.tabs([
        "📋 Listado y Buscador", 
        "➕ Registrar Cliente", 
        "✏️ Editar", 
        "🗑️ Eliminar"
    ])

    # -------------------------------------------------------------------------
    # PESTAÑA 1: LISTAR CLIENTES Y BUSCADOR RÁPIDO
    # -------------------------------------------------------------------------
    with tab_listar:
        st.subheader("🏢 Registro de Clientes")

        # Buscador rápido por nombre o empresa
        busqueda = st.text_input("🔍 Buscar cliente por nombre o empresa:", "", key="input_busqueda_clientes")

        # Filtrar lista de clientes según coincidencia de texto
        if busqueda:
            clientes_filtrados = [
                c for c in clientes 
                if busqueda.lower() in c.get("nombre", "").lower() or busqueda.lower() in c.get("empresa", "").lower()
            ]
        else:
            clientes_filtrados = clientes

        if not clientes_filtrados:
            st.info("No hay clientes registrados o que coincidan con el criterio de búsqueda.")
        else:
            # Normalización y mapeo flexible de campos para construir el DataFrame
            datos_display = []
            for c in clientes_filtrados:
                # Soportar ambas nomenclaturas posibles (contacto/telefono y correo/email)
                tel = c.get("contacto") if c.get("contacto") is not None else c.get("telefono", "-")
                email = c.get("correo") if c.get("correo") is not None else c.get("email", "-")

                datos_display.append({
                    "id": c.get("id", "-"),
                    "nombre": c.get("nombre", "-"),
                    "empresa": c.get("empresa", "-"),
                    "email": email,
                    "telefono": tel
                })

            df_clientes = pd.DataFrame(datos_display)

            # Renombrar columnas para la presentación en la interfaz
            df_clientes = df_clientes.rename(columns={
                "id": "ID",
                "nombre": "Nombre Contacto",
                "empresa": "Empresa / Organización",
                "email": "Correo Electrónico",
                "telefono": "Teléfono / Celular"
            })

            # Mostrar tabla interactiva con Streamlit
            st.dataframe(
                df_clientes,
                use_container_width=True,
                hide_index=True
            )

    # -------------------------------------------------------------------------
    # PESTAÑA 2: REGISTRAR CLIENTE
    # -------------------------------------------------------------------------
    with tab_crear:
        st.subheader("Formulario de Registro")
        with st.form("form_nuevo_cliente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del Contacto*")
                empresa = st.text_input("Nombre de la Empresa*")
            with col2:
                contacto = st.text_input("Teléfono / Celular")
                correo = st.text_input("Correo Electrónico")

            submit = st.form_submit_button("Guardar Cliente")

            if submit:
                if not nombre.strip() or not empresa.strip():
                    st.error("Los campos 'Nombre' y 'Empresa' son obligatorios.")
                else:
                    nuevo_cliente = {
                        "id": str(uuid.uuid4())[:8],  # ID único de 8 caracteres
                        "nombre": nombre.strip(),
                        "empresa": empresa.strip(),
                        "contacto": contacto.strip(),
                        "correo": correo.strip()
                    }
                    clientes.append(nuevo_cliente)
                    guardar_json(CLIENTES_FILE, clientes)
                    st.success(f"Cliente '{empresa}' registrado correctamente.")
                    st.rerun()

    # -------------------------------------------------------------------------
    # PESTAÑA 3: EDITAR CLIENTE
    # -------------------------------------------------------------------------
    with tab_editar:
        st.subheader("Editar Datos de Cliente")
        if not clientes:
            st.info("No hay clientes disponibles para editar.")
        else:
            # Selector por empresa/nombre
            opciones_clientes = {
                f"{c.get('empresa', 'Sin Empresa')} ({c.get('nombre', 'Sin Nombre')})": c 
                for c in clientes
            }
            cliente_sel_key = st.selectbox("Selecciona un cliente:", list(opciones_clientes.keys()), key="select_editar_cliente")
            cliente_sel = opciones_clientes[cliente_sel_key]

            # Obtención de valores iniciales considerando compatibilidad de llaves
            val_contacto = cliente_sel.get("contacto") if cliente_sel.get("contacto") is not None else cliente_sel.get("telefono", "")
            val_correo = cliente_sel.get("correo") if cliente_sel.get("correo") is not None else cliente_sel.get("email", "")

            with st.form("form_editar_cliente"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_nombre = st.text_input("Nombre del Contacto", value=cliente_sel.get("nombre", ""))
                    nueva_empresa = st.text_input("Empresa", value=cliente_sel.get("empresa", ""))
                with col2:
                    nuevo_contacto = st.text_input("Teléfono / Celular", value=val_contacto)
                    nuevo_correo = st.text_input("Correo Electrónico", value=val_correo)

                btn_actualizar = st.form_submit_button("Actualizar Cliente")

                if btn_actualizar:
                    if not nuevo_nombre.strip() or not nueva_empresa.strip():
                        st.error("Los campos 'Nombre' y 'Empresa' no pueden estar vacíos.")
                    else:
                        # Actualizar datos en memoria
                        cliente_sel["nombre"] = nuevo_nombre.strip()
                        cliente_sel["empresa"] = nueva_empresa.strip()
                        cliente_sel["contacto"] = nuevo_contacto.strip()
                        cliente_sel["correo"] = nuevo_correo.strip()

                        # Si existían las claves antiguas, las estandarizamos
                        if "telefono" in cliente_sel:
                            cliente_sel["telefono"] = nuevo_contacto.strip()
                        if "email" in cliente_sel:
                            cliente_sel["email"] = nuevo_correo.strip()

                        guardar_json(CLIENTES_FILE, clientes)
                        st.success("Información del cliente actualizada correctamente.")
                        st.rerun()

    # -------------------------------------------------------------------------
    # PESTAÑA 4: ELIMINAR CLIENTE
    # -------------------------------------------------------------------------
    with tab_eliminar:
        st.subheader("Eliminar Cliente")
        if not clientes:
            st.info("No hay clientes registrados para eliminar.")
        else:
            opciones_eliminar = {
                f"{c.get('empresa', 'Sin Empresa')} ({c.get('nombre', 'Sin Nombre')})": c 
                for c in clientes
            }
            cliente_del_key = st.selectbox("Selecciona el cliente a eliminar:", list(opciones_eliminar.keys()), key="select_del_cliente")
            cliente_del = opciones_eliminar[cliente_del_key]

            st.warning(f"⚠️ ¿Estás seguro de eliminar a **{cliente_del.get('empresa')}**? Esta acción no se puede deshacer.")
            
            if st.button("Confirmar Eliminación", type="primary", key="btn_confirmar_eliminar_cliente"):
                # Filtrar lista para remover el cliente seleccionado
                clientes_actualizados = [c for c in clientes if c.get("id") != cliente_del.get("id")]
                guardar_json(CLIENTES_FILE, clientes_actualizados)
                st.success(f"Cliente '{cliente_del.get('empresa')}' eliminado con éxito.")
                st.rerun()