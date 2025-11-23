import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from typing import List, Dict, Any, Optional
import logging

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class DataVisualizer:
    """Generador de visualizaciones avanzadas para análisis de datos"""
    
    def __init__(self, style: str = 'seaborn'):
        self.style = style
        self._setup_styles()
    
    def _setup_styles(self):
        """Configura estilos para las visualizaciones"""
        if self.style == 'seaborn':
            sns.set_theme(style="whitegrid")
            plt.rcParams['figure.figsize'] = (12, 8)
            plt.rcParams['font.size'] = 12
    
    def create_comprehensive_dashboard(self, df: pd.DataFrame, sales_col: str = None, 
                                    category_col: str = None) -> go.Figure:
        """Crea un dashboard completo con múltiples visualizaciones"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            logger.warning("No hay columnas numéricas para visualizar")
            return None
        
        # Determinar columnas automáticamente si no se especifican
        if not sales_col:
            sales_col = self._find_sales_column(df)
        if not category_col:
            category_col = self._find_category_column(df)
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Distribución de Ventas', 
                'Top 10 Productos por Ventas',
                'Análisis de Stock vs Ventas',
                'Valores Atípicos'
            ),
            specs=[[{"type": "histogram"}, {"type": "bar"}],
                  [{"type": "scatter"}, {"type": "box"}]]
        )
        
        # 1. Histograma de ventas
        if sales_col and sales_col in df.columns:
            fig.add_trace(
                go.Histogram(x=df[sales_col], name="Distribución Ventas"),
                row=1, col=1
            )
        
        # 2. Top productos
        if sales_col and category_col:
            top_products = df.groupby(category_col)[sales_col].sum().nlargest(10)
            fig.add_trace(
                go.Bar(x=top_products.index, y=top_products.values, name="Top Productos"),
                row=1, col=2
            )
        
        # 3. Scatter plot stock vs ventas
        stock_col = self._find_stock_column(df)
        if sales_col and stock_col:
            fig.add_trace(
                go.Scatter(x=df[sales_col], y=df[stock_col], mode='markers', 
                          name="Stock vs Ventas"),
                row=2, col=1
            )
        
        # 4. Box plot para outliers
        if sales_col:
            fig.add_trace(
                go.Box(y=df[sales_col], name="Ventas"),
                row=2, col=2
            )
        
        fig.update_layout(height=800, title_text="Dashboard de Análisis Completo")
        return fig
    
    def create_sales_analysis_plots(self, df: pd.DataFrame, sales_col: str, 
                                  category_col: str = None) -> Dict[str, go.Figure]:
        """Crea múltiples visualizaciones para análisis de ventas"""
        plots = {}
        
        # 1. Distribución de ventas
        plots['distribution'] = px.histogram(
            df, x=sales_col, 
            title=f'Distribución de {sales_col}',
            nbins=50
        )
        
        # 2. Top productos/categorías
        if category_col:
            top_categories = df.groupby(category_col)[sales_col].sum().nlargest(15)
            plots['top_categories'] = px.bar(
                x=top_categories.index, y=top_categories.values,
                title=f'Top 15 {category_col} por Ventas',
                labels={'x': category_col, 'y': 'Ventas Totales'}
            )
        
        # 3. Análisis de outliers
        Q1 = df[sales_col].quantile(0.25)
        Q3 = df[sales_col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_mask = (df[sales_col] < (Q1 - 1.5 * IQR)) | (df[sales_col] > (Q3 + 1.5 * IQR))
        
        plots['outliers'] = px.box(df, y=sales_col, title=f'Box Plot - {sales_col}')
        
        # 4. Heatmap de correlaciones (si hay múltiples columnas numéricas)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            plots['correlation'] = px.imshow(
                corr_matrix, 
                title='Matriz de Correlación',
                aspect='auto',
                color_continuous_scale='RdBu_r'
            )
        
        return plots
    
    def create_stock_analysis_plots(self, df: pd.DataFrame, stock_col: str, 
                                  sales_col: str = None) -> Dict[str, go.Figure]:
        """Crea visualizaciones para análisis de inventario"""
        plots = {}
        
        # 1. Distribución de stock
        plots['stock_distribution'] = px.histogram(
            df, x=stock_col, 
            title=f'Distribución de {stock_col}',
            nbins=30
        )
        
        # 2. Análisis ABC de inventario
        if sales_col:
            # Calcular porcentaje acumulado
            df_sorted = df.sort_values(sales_col, ascending=False)
            df_sorted['cumulative_percentage'] = df_sorted[sales_col].cumsum() / df_sorted[sales_col].sum() * 100
            
            plots['abc_analysis'] = px.line(
                df_sorted, y='cumulative_percentage',
                title='Análisis ABC - Curva de Pareto',
                labels={'index': 'Productos', 'cumulative_percentage': '% Acumulado Ventas'}
            )
        
        # 3. Stock vs Ventas (si ambas columnas existen)
        if sales_col and stock_col:
            plots['stock_vs_sales'] = px.scatter(
                df, x=sales_col, y=stock_col,
                title=f'{stock_col} vs {sales_col}',
                trendline="lowess"
            )
        
        # 4. Alertas de stock bajo
        low_stock_threshold = 5
        low_stock = df[df[stock_col] <= low_stock_threshold]
        
        if len(low_stock) > 0:
            plots['low_stock_alert'] = px.bar(
                low_stock, x=stock_col, y=low_stock.index,
                title=f'Productos con Stock Bajo (<={low_stock_threshold})',
                orientation='h'
            )
        
        return plots
    
    def create_trend_analysis(self, df: pd.DataFrame, date_col: str = None, 
                            value_col: str = None) -> Optional[go.Figure]:
        """Análisis de tendencias temporales (si existe columna de fecha)"""
        if not date_col:
            date_col = self._find_date_column(df)
        
        if not date_col or not value_col:
            logger.warning("No se encontraron columnas de fecha o valores para análisis de tendencias")
            return None
        
        try:
            # Convertir a datetime si es posible
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_trend = df.dropna(subset=[date_col, value_col])
            
            if len(df_trend) == 0:
                return None
            
            # Agrupar por tiempo (mensual)
            df_trend['month'] = df_trend[date_col].dt.to_period('M')
            monthly_data = df_trend.groupby('month')[value_col].sum().reset_index()
            monthly_data['month'] = monthly_data['month'].astype(str)
            
            fig = px.line(
                monthly_data, x='month', y=value_col,
                title=f'Tendencia Mensual de {value_col}',
                markers=True
            )
            
            return fig
        except Exception as e:
            logger.warning(f"No se pudo crear análisis de tendencias: {e}")
            return None
    
    def _find_sales_column(self, df: pd.DataFrame) -> Optional[str]:
        """Encuentra automáticamente la columna de ventas"""
        sales_keywords = ['venta', 'sales', 'venda', 'cajas vend', 'unidades']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in sales_keywords):
                return col
        return None
    
    def _find_stock_column(self, df: pd.DataFrame) -> Optional[str]:
        """Encuentra automáticamente la columna de stock"""
        stock_keywords = ['stock', 'inventario', 'cajas stock', 'inventory']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in stock_keywords):
                return col
        return None
    
    def _find_category_column(self, df: pd.DataFrame) -> Optional[str]:
        """Encuentra automáticamente la columna de categoría"""
        category_keywords = ['categoria', 'category', 'rubro', 'departamento', 'laboratorio']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in category_keywords):
                return col
        return None
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Encuentra automáticamente la columna de fecha"""
        date_keywords = ['fecha', 'date', 'periodo', 'mes', 'dia']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in date_keywords):
                return col
        
        # Buscar columnas que parezcan fechas
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = df[col].dropna().head(10)
                if any('/' in str(x) or '-' in str(x) for x in sample):
                    return col
        
        return None
    
    def export_plots(self, plots: Dict[str, go.Figure], output_dir: str = 'outputs/plots'):
        """Exporta todas las visualizaciones a archivos HTML"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for name, fig in plots.items():
            filename = f"{output_dir}/{name}.html"
            fig.write_html(filename)
            logger.info(f"Visualización guardada: {filename}")