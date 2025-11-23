# 🚀 Analytics Suite - Sistema Profesional de Análisis de Datos

**Sistema modular y escalable para análisis de ventas, inventario y business intelligence**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.24%2B-red)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-orange)](https://pandas.pydata.org)

## 📊 Descripción

Analytics Suite es un sistema profesional diseñado para el análisis de datos de ventas e inventario, especialmente optimizado para el sector farmacéutico. Ofrece tanto interfaz web interactiva como modo consola para análisis batch.

## ✨ Características Principales

### 🔧 Módulos del Sistema
- **`DataLoader`**: Carga inteligente con detección automática de encoding y delimitadores
- **`DataAnalyzer`**: Análisis avanzado de ventas, stock y tendencias
- **`DataVisualizer`**: Visualizaciones interactivas con Plotly
- **`ReportGenerator`**: Reportes profesionales en Excel y HTML

### 🎯 Funcionalidades
- ✅ **Análisis de ventas** por laboratorio, rubro y período
- ✅ **Gestión de inventario** con alertas de stock bajo
- ✅ **Dashboard interactivo** con Streamlit
- ✅ **Reportes exportables** en múltiples formatos
- ✅ **Detección de anomalías** y outliers
- ✅ **Recomendaciones automáticas** para reposición
- ✅ **Visualizaciones avanzadas** y análisis ABC

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

🔧 Módulos Principales
----------------------

### DataLoader

Carga inteligente de datasets con:

*   Detección automática de encoding
    
*   Identificación de delimitadores
    
*   Validación de formato y tamaño
    
*   Post-procesamiento automático
    

### DataAnalyzer

Análisis comprehensivo incluyendo:

*   Estadísticas descriptivas
    
*   Análisis de ventas por categoría
    
*   Gestión de inventario y stock
    
*   Detección de anomalías
    
*   Recomendaciones automáticas
    

### DataVisualizer

Visualizaciones interactivas con:

*   Gráficos de barras y distribución
    
*   Análisis de correlación
    
*   Dashboards interactivos
    
*   Exportación a HTML
    

### ReportGenerator

Generación de reportes profesionales:

*   Reportes en Excel con múltiples hojas
    
*   Formatos HTML para web
    
*   Métricas ejecutivas y detalladas
    
*   Alertas y recomendaciones
    

🎨 Dashboard Web
----------------

El dashboard Streamlit ofrece:

### 📊 Resumen General

*   Métricas clave de ventas y stock
    
*   Vista general del dataset
    
*   Información de laboratorios y productos
    

### 🧪 Análisis Interactivo

*   Filtros por laboratorio y categoría
    
*   Visualizaciones en tiempo real
    
*   Análisis de tendencias
    

### 🚨 Panel de Alertas

*   Productos con stock bajo
    
*   Items sin movimiento
    
*   Recomendaciones del sistema
    

### 💾 Generación de Reportes

*   Reportes completos en Excel
    
*   Exportación rápida de datos
    
*   Descarga directa desde el navegador
    

📊 Formatos Soportados
----------------------

### Entrada

*   ✅ CSV (con detección automática de delimitadores)
    
*   ✅ Excel (.xlsx, .xls)
    
*   ✅ Encoding: UTF-8, Latin-1, detección automática
    

### Salida

*   ✅ Excel (.xlsx) con múltiples hojas
    
*   ✅ HTML para visualización web
    
*   ✅ Gráficos interactivos (Plotly)

### Instalación de dependencias
```bash
pip install -r requirements.txt
#Dashboard Web
streamlit run app.py
#Modo Consola
python main.py
