import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.data_analyzer import DataAnalyzer
from src.visualization import DataVisualizer
from src.report_generator import ReportGenerator

def main():
    st.set_page_config(
        page_title="Analytics Suite - Farmacia",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("💊 Analytics Suite - Sistema de Análisis para Farmacia")
    st.markdown("---")
    
    # Sidebar para carga de archivos
    with st.sidebar:
        st.header("📁 Cargar Datos")
        uploaded_file = st.file_uploader(
            "Sube tu archivo CSV de farmacia",
            type=['csv'],
            help="Formatos soportados: CSV"
        )
        
        if uploaded_file is not None:
            # Guardar archivo temporalmente
            with open("temp_data.csv", "wb") as f:
                f.write(uploaded_file.getvalue())
            
            st.success("✅ Archivo cargado exitosamente!")
            st.info(f"📊 {uploaded_file.name} listo para análisis")
    
    # Contenido principal
    if uploaded_file is not None:
        try:
            # Cargar datos - CORREGIDO: usar smart_load en lugar de load_farmacia_format
            with st.spinner("Cargando y analizando datos..."):
                loader = DataLoader()
                df = loader.smart_load("temp_data.csv")  # ✅ CORREGIDO
                
                # Limpiar archivo temporal
                if os.path.exists("temp_data.csv"):
                    os.remove("temp_data.csv")
            
            # Mostrar información básica
            st.subheader("📈 Resumen General")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Productos", len(df))
            with col2:
                # Buscar columna de laboratorio de forma segura
                lab_cols = [col for col in df.columns if 'laboratorio' in col.lower()]
                laboratorios = df[lab_cols[0]].nunique() if lab_cols else "N/A"
                st.metric("Laboratorios", laboratorios)
            with col3:
                # Buscar columna de ventas de forma segura
                sales_cols = [col for col in df.columns if 'vend' in col.lower() and 'total' in col.lower()]
                total_ventas = df[sales_cols[0]].sum() if sales_cols else 0
                st.metric("Ventas Totales", f"{total_ventas:,.0f}")
            with col4:
                # Buscar columna de stock de forma segura
                stock_cols = [col for col in df.columns if 'stock' in col.lower() and 'total' in col.lower()]
                total_stock = df[stock_cols[0]].sum() if stock_cols else 0
                st.metric("Stock Total", f"{total_stock:,.0f}")
            
            # Pestañas de análisis
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Vista de Datos", "🧪 Análisis", "🚨 Alertas", "💾 Reportes"
            ])
            
            with tab1:
                show_data_view(df)
            
            with tab2:
                show_analysis(df)
            
            with tab3:
                show_alerts(df)
            
            with tab4:
                show_reports(df)
                
        except Exception as e:
            st.error(f"❌ Error procesando el archivo: {str(e)}")
            st.info("💡 Asegúrate de que el archivo CSV tenga el formato correcto")
    
    else:
        # Pantalla de bienvenida
        st.info("👆 Por favor, sube un archivo CSV para comenzar el análisis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Formato Esperado")
            st.markdown("""
            El sistema espera un CSV con columnas como:
            - **Producto**: Nombre del producto
            - **Laboratorio**: Fabricante/Laboratorio  
            - **Rubro**: Categoría del producto
            - **Cajas Vend. Total**: Ventas totales
            - **Cajas Stock Total**: Stock actual
            - **Costo**: Precio de costo
            - **PVP**: Precio de venta
            """)
        
        with col2:
            st.subheader("🚀 Funcionalidades")
            st.markdown("""
            - ✅ **Análisis de ventas** por laboratorio y rubro
            - ✅ **Gestión de inventario** y alertas de stock
            - ✅ **Visualizaciones interactivas**
            - ✅ **Reportes exportables** en Excel
            - ✅ **Detección de anomalías**
            - ✅ **Recomendaciones automáticas**
            """)

def show_data_view(df):
    """Vista de datos crudos"""
    st.subheader("📋 Vista de Datos")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        rows_to_show = st.slider("Filas a mostrar", 5, 100, 10)
    with col2:
        # Buscar columna de laboratorio de forma segura
        lab_cols = [col for col in df.columns if 'laboratorio' in col.lower()]
        if lab_cols:
            laboratorios = ['Todos'] + list(df[lab_cols[0]].unique())
            selected_lab = st.selectbox("Filtrar por Laboratorio", laboratorios)
            if selected_lab != 'Todos':
                df = df[df[lab_cols[0]] == selected_lab]
    
    # Mostrar datos
    st.dataframe(df.head(rows_to_show), use_container_width=True)
    
    # Información del dataset
    with st.expander("📊 Información del Dataset"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Forma:**", df.shape)
            st.write("**Columnas:**", list(df.columns))
        with col2:
            st.write("**Tipos de datos:**")
            for col, dtype in df.dtypes.items():
                st.write(f"- {col}: {dtype}")

def show_analysis(df):
    """Análisis de datos"""
    st.subheader("🧪 Análisis de Datos")
    
    try:
        analyzer = DataAnalyzer(df)
        analysis = analyzer.comprehensive_analysis()
        
        # Métricas clave
        col1, col2, col3 = st.columns(3)
        
        with col1:
            low_stock = len(analyzer._identify_low_stock())
            st.metric("Productos Stock Bajo", low_stock)
        
        with col2:
            if 'sales_analysis' in analysis:
                sales_data = list(analysis['sales_analysis'].values())[0]
                zero_sales = sales_data.get('zero_sales', 0) if isinstance(sales_data, dict) else 0
                st.metric("Productos Sin Ventas", zero_sales)
        
        with col3:
            missing_values = analysis['basic_stats']['missing_values']
            st.metric("Valores Faltantes", missing_values)
        
        # Análisis por laboratorio
        lab_cols = [col for col in df.columns if 'laboratorio' in col.lower()]
        sales_cols = [col for col in df.columns if 'vend' in col.lower() and 'total' in col.lower()]
        
        if lab_cols and sales_cols:
            st.subheader("📊 Ventas por Laboratorio")
            lab_sales = df.groupby(lab_cols[0])[sales_cols[0]].sum().sort_values(ascending=False)
            st.bar_chart(lab_sales.head(10))
        
        # Distribución de stock
        stock_cols = [col for col in df.columns if 'stock' in col.lower() and 'total' in col.lower()]
        if stock_cols:
            st.subheader("📦 Distribución de Stock")
            st.bar_chart(df[stock_cols[0]].value_counts().head(10))
            
    except Exception as e:
        st.error(f"Error en el análisis: {e}")

def show_alerts(df):
    """Panel de alertas"""
    st.subheader("🚨 Alertas y Recomendaciones")
    
    try:
        analyzer = DataAnalyzer(df)
        
        # Alertas de stock bajo
        low_stock = analyzer._identify_low_stock(threshold=5)
        if len(low_stock) > 0:
            st.warning(f"**{len(low_stock)} productos con stock bajo (≤ 5 unidades)**")
            
            # Mostrar productos críticos
            display_cols = []
            for col in low_stock.columns:
                if any(keyword in col.lower() for keyword in ['producto', 'laboratorio', 'stock', 'vend']):
                    display_cols.append(col)
            
            if display_cols:
                # Ordenar por stock (menor primero)
                stock_col = [col for col in display_cols if 'stock' in col.lower()][0] if any('stock' in col.lower() for col in display_cols) else display_cols[0]
                st.dataframe(low_stock[display_cols].sort_values(stock_col))
        else:
            st.success("✅ No hay productos con stock crítico")
        
        # Productos sin ventas
        sales_cols = [col for col in df.columns if 'vend' in col.lower() and 'total' in col.lower()]
        if sales_cols:
            no_sales = df[df[sales_cols[0]] == 0]
            if len(no_sales) > 0:
                st.info(f"**{len(no_sales)} productos sin ventas registradas**")
                
                display_cols = []
                for col in no_sales.columns:
                    if any(keyword in col.lower() for keyword in ['producto', 'laboratorio', 'stock']):
                        display_cols.append(col)
                
                if display_cols:
                    st.dataframe(no_sales[display_cols].head(10))
        
        # Análisis de recomendaciones
        analysis = analyzer.comprehensive_analysis()
        recommendations = analysis.get('recommendations', [])
        
        if recommendations:
            st.subheader("💡 Recomendaciones del Sistema")
            for rec in recommendations:
                st.write(f"• {rec}")
                
    except Exception as e:
        st.error(f"Error generando alertas: {e}")

def show_reports(df):
    """Generación de reportes"""
    st.subheader("💾 Generación de Reportes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generar Reporte Completo", type="primary"):
            with st.spinner("Generando reporte completo..."):
                try:
                    analyzer = DataAnalyzer(df)
                    analysis = analyzer.comprehensive_analysis()
                    reporter = ReportGenerator()
                    report_path = reporter.generate_comprehensive_report(df, analysis)
                    
                    st.success(f"✅ Reporte generado: {report_path}")
                    
                    # Ofrecer descarga
                    with open(report_path, "rb") as file:
                        st.download_button(
                            label="📥 Descargar Reporte Completo",
                            data=file,
                            file_name=os.path.basename(report_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error generando reporte: {e}")
    
    with col2:
        if st.button("⚡ Reporte Rápido"):
            with st.spinner("Generando reporte rápido..."):
                try:
                    reporter = ReportGenerator()
                    report_path = reporter.generate_quick_report(df)
                    
                    st.success(f"✅ Reporte rápido generado: {report_path}")
                    
                    with open(report_path, "rb") as file:
                        st.download_button(
                            label="📥 Descargar Reporte Rápido",
                            data=file,
                            file_name=os.path.basename(report_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error generando reporte rápido: {e}")

if __name__ == "__main__":
    main()