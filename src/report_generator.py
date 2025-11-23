import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generador de reportes profesionales en múltiples formatos"""
    
    def __init__(self, output_dir: str = 'outputs/reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_comprehensive_report(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                                   format: str = 'excel') -> str:
        """Genera un reporte completo en el formato especificado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == 'excel':
            return self._generate_excel_report(df, analysis_results, timestamp)
        elif format.lower() == 'html':
            return self._generate_html_report(df, analysis_results, timestamp)
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def _generate_excel_report(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                             timestamp: str) -> str:
        """Genera reporte en formato Excel con múltiples hojas"""
        filename = self.output_dir / f"analytics_report_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 1. Hoja: Datos Originales
            df.to_excel(writer, sheet_name='Datos_Originales', index=False)
            
            # 2. Hoja: Resumen Ejecutivo
            self._create_executive_summary(df, analysis_results, writer)
            
            # 3. Hoja: Análisis de Ventas
            self._create_sales_analysis_sheet(df, analysis_results, writer)
            
            # 4. Hoja: Análisis de Stock
            self._create_stock_analysis_sheet(df, analysis_results, writer)
            
            # 5. Hoja: Alertas y Recomendaciones
            self._create_alerts_sheet(df, analysis_results, writer)
            
            # 6. Hoja: Métricas Detalladas
            self._create_metrics_sheet(df, analysis_results, writer)
        
        logger.info(f"📊 Reporte Excel generado: {filename}")
        return str(filename)
    
    def _create_executive_summary(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                                writer: pd.ExcelWriter):
        """Crea hoja de resumen ejecutivo"""
        summary_data = []
        
        # Información básica
        basic_stats = analysis_results.get('basic_stats', {})
        summary_data.append(('Total Filas', basic_stats.get('total_rows', len(df))))
        summary_data.append(('Total Columnas', basic_stats.get('total_columns', len(df.columns))))
        summary_data.append(('Productos Únicos', df.iloc[:, 0].nunique() if len(df.columns) > 0 else 0))
        
        # Análisis de ventas
        sales_analysis = analysis_results.get('sales_analysis', {})
        if sales_analysis:
            for col, stats in sales_analysis.items():
                if isinstance(stats, dict):
                    summary_data.append((f'Total Ventas ({col})', stats.get('total', 0)))
                    summary_data.append((f'Productos sin Ventas ({col})', stats.get('zero_sales', 0)))
        
        # Análisis de stock
        inventory_analysis = analysis_results.get('inventory_analysis', {})
        if inventory_analysis:
            low_stock = inventory_analysis.get('low_stock_items', [])
            summary_data.append(('Productos Stock Bajo', len(low_stock)))
        
        # Recomendaciones
        recommendations = analysis_results.get('recommendations', [])
        summary_data.append(('Recomendaciones Críticas', len(recommendations)))
        
        summary_df = pd.DataFrame(summary_data, columns=['Métrica', 'Valor'])
        summary_df.to_excel(writer, sheet_name='Resumen_Ejecutivo', index=False)
        
        # Formatear la hoja
        workbook = writer.book
        worksheet = writer.sheets['Resumen_Ejecutivo']
        
        # Ajustar ancho de columnas
        worksheet.column_dimensions['A'].width = 30
        worksheet.column_dimensions['B'].width = 20
    
    def _create_sales_analysis_sheet(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                                   writer: pd.ExcelWriter):
        """Crea hoja de análisis de ventas"""
        sales_data = []
        
        # Encontrar columnas de ventas
        sales_cols = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['venta', 'sales', 'venda'])]
        
        for col in sales_cols:
            if df[col].dtype in [np.int64, np.float64]:
                sales_stats = {
                    'Columna': col,
                    'Total': df[col].sum(),
                    'Promedio': df[col].mean(),
                    'Mediana': df[col].median(),
                    'Máximo': df[col].max(),
                    'Mínimo': df[col].min(),
                    'Desviación Estándar': df[col].std(),
                    'Productos con Ventas > 0': (df[col] > 0).sum(),
                    'Productos sin Ventas': (df[col] == 0).sum()
                }
                sales_data.append(sales_stats)
        
        if sales_data:
            sales_df = pd.DataFrame(sales_data)
            sales_df.to_excel(writer, sheet_name='Analisis_Ventas', index=False)
    
    def _create_stock_analysis_sheet(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                                   writer: pd.ExcelWriter):
        """Crea hoja de análisis de stock"""
        stock_data = []
        
        # Encontrar columnas de stock
        stock_cols = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['stock', 'inventario'])]
        
        for col in stock_cols:
            if df[col].dtype in [np.int64, np.float64]:
                stock_stats = {
                    'Columna': col,
                    'Total Stock': df[col].sum(),
                    'Promedio Stock': df[col].mean(),
                    'Productos sin Stock': (df[col] == 0).sum(),
                    'Productos Stock Bajo (<5)': ((df[col] > 0) & (df[col] <= 5)).sum(),
                    'Productos Stock Medio (6-20)': ((df[col] > 5) & (df[col] <= 20)).sum(),
                    'Productos Stock Alto (>20)': (df[col] > 20).sum(),
                    'Stock Máximo': df[col].max()
                }
                stock_data.append(stock_stats)
        
        if stock_data:
            stock_df = pd.DataFrame(stock_data)
            stock_df.to_excel(writer, sheet_name='Analisis_Stock', index=False)
            
            # Lista de productos con stock bajo
            low_stock_threshold = 5
            for col in stock_cols:
                low_stock = df[df[col] <= low_stock_threshold]
                if len(low_stock) > 0:
                    low_stock.to_excel(writer, sheet_name='Stock_Bajo_Alerta', index=False)
                    break
    
    def _create_alerts_sheet(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                           writer: pd.ExcelWriter):
        """Crea hoja de alertas y recomendaciones"""
        alerts_data = []
        
        # Alertas de stock bajo
        stock_cols = [col for col in df.columns if 'stock' in col.lower()]
        if stock_cols:
            low_stock = df[df[stock_cols[0]] <= 5]
            for _, product in low_stock.iterrows():
                alerts_data.append({
                    'Tipo': 'STOCK BAJO',
                    'Producto': product.get('Producto', 'N/A'),
                    'Stock Actual': product[stock_cols[0]],
                    'Recomendación': 'REPONER URGENTE'
                })
        
        # Alertas de productos sin ventas
        sales_cols = [col for col in df.columns if 'vent' in col.lower()]
        if sales_cols:
            no_sales = df[df[sales_cols[0]] == 0]
            for _, product in no_sales.head(20).iterrows():  # Limitar a top 20
                alerts_data.append({
                    'Tipo': 'SIN VENTAS',
                    'Producto': product.get('Producto', 'N/A'),
                    'Stock Actual': product.get(stock_cols[0], 'N/A') if stock_cols else 'N/A',
                    'Recomendación': 'REVISAR ROTACIÓN'
                })
        
        # Recomendaciones del análisis
        recommendations = analysis_results.get('recommendations', [])
        for rec in recommendations:
            alerts_data.append({
                'Tipo': 'RECOMENDACIÓN',
                'Producto': 'SISTEMA',
                'Stock Actual': 'N/A',
                'Recomendación': rec
            })
        
        if alerts_data:
            alerts_df = pd.DataFrame(alerts_data)
            alerts_df.to_excel(writer, sheet_name='Alertas_Recomendaciones', index=False)
    
    def _create_metrics_sheet(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                            writer: pd.ExcelWriter):
        """Crea hoja con métricas detalladas"""
        metrics_data = []
        
        # Métricas por columna numérica
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            metrics = {
                'Columna': col,
                'Tipo': 'Numérica',
                'Valores Únicos': df[col].nunique(),
                'Valores Faltantes': df[col].isnull().sum(),
                'Porcentaje Faltantes': (df[col].isnull().sum() / len(df)) * 100,
                'Media': df[col].mean(),
                'Mediana': df[col].median(),
                'Desviación Estándar': df[col].std(),
                'Asimetría': df[col].skew(),
                'Curtosis': df[col].kurtosis()
            }
            metrics_data.append(metrics)
        
        # Métricas por columna categórica
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            metrics = {
                'Columna': col,
                'Tipo': 'Categórica',
                'Valores Únicos': df[col].nunique(),
                'Valores Faltantes': df[col].isnull().sum(),
                'Porcentaje Faltantes': (df[col].isnull().sum() / len(df)) * 100,
                'Valor Más Frecuente': df[col].mode().iloc[0] if not df[col].mode().empty else 'N/A',
                'Frecuencia Máxima': df[col].value_counts().max() if not df[col].empty else 0
            }
            metrics_data.append(metrics)
        
        if metrics_data:
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_excel(writer, sheet_name='Metricas_Detalladas', index=False)
    
    def _generate_html_report(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                            timestamp: str) -> str:
        """Genera reporte en formato HTML (para implementación futura)"""
        filename = self.output_dir / f"analytics_report_{timestamp}.html"
        
        # Implementación básica - se puede expandir
        html_content = f"""
        <html>
        <head>
            <title>Analytics Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f5f5f5; padding: 10px; margin: 5px; border-radius: 5px; }}
                .alert {{ background: #ffe6e6; padding: 10px; margin: 5px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>📊 Analytics Report</h1>
            <p>Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <h2>Resumen Ejecutivo</h2>
            <div class="metric">
                <strong>Total de Productos:</strong> {len(df)}<br>
                <strong>Columnas Analizadas:</strong> {len(df.columns)}
            </div>
            
            <h2>Recomendaciones</h2>
            {"".join(f'<div class="alert">{rec}</div>' for rec in analysis_results.get('recommendations', []))}
        </body>
        </html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📄 Reporte HTML generado: {filename}")
        return str(filename)
    
    def generate_quick_report(self, df: pd.DataFrame, output_format: str = 'excel') -> str:
        """Genera un reporte rápido sin análisis complejo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"quick_report_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Datos originales
            df.to_excel(writer, sheet_name='Datos', index=False)
            
            # Resumen estadístico
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df[numeric_cols].describe().to_excel(writer, sheet_name='Estadisticas')
            
            # Top productos por primera columna numérica
            if len(numeric_cols) > 0:
                top_col = numeric_cols[0]
                top_products = df.nlargest(20, top_col)
                top_products.to_excel(writer, sheet_name=f'Top_20_{top_col}', index=False)
        
        logger.info(f"⚡ Reporte rápido generado: {filename}")
        return str(filename)