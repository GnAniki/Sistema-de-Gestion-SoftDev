# 🚀 Sistema de Gestión Interna — SoftDev

Sistema web local para la gestión de clientes, proyectos y tareas con generación de reportes inteligentes mediante IA local.

---

## 🛠️ Requisitos Previos e Instalación

tener instalado lo siguiente:
-python versiones actuales
-Git


### 1. Clonar el repositorio
```bash
git clone [https://github.com/GnAniki/Sistema-de-Gestion-SoftDev.git](https://github.com/GnAniki/Sistema-de-Gestion-SoftDev.git)
cd Sistema-de-Gestion-SoftDev

2. Crear y activar entorno virtual (Recomendado)
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / Mac
python -m venv venv
source venv/bin/activate

3. Instalar librerías necesarias

pip install streamlit pandas requests

🤖 Configuración de IA Local (Ollama)

El módulo de reportes inteligentes requiere tener instalado Ollama de forma local.

Descarga e instala Ollama desde: ollama.com

Asegúrate de ejecutar el modelo Phi-3 Mini descargándolo desde tu terminal:

ollama run phi3

Verifica que Ollama esté corriendo en segundo plano en http://localhost:11434

Ejecución del Sistema

streamlit run app.py

📂 Estructura de Módulos
🏠 Inicio: Dashboard con métricas globales y gráficos.

👥 Clientes: Directorio y gestión CRUD de clientes.

📁 Proyectos: Control de fechas, presupuestos y estado de proyectos.

✅ Tareas: Asignación por responsable y prioridades (Alta/Media/Baja).

🤖 Asistente IA: Generación de reportes ejecutivos usando Ollama.
