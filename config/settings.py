import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AnalysisConfig:
    """Configuración para el análisis de datos"""
    
    # Formatos soportados
    SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls']
    DEFAULT_ENCODING = 'utf-8'
    MAX_FILE_SIZE_MB = 100
    
    # Umbrales para análisis
    STOCK_ALERT_THRESHOLD = 5
    TOP_N_PRODUCTS = 20
    OUTLIER_THRESHOLD = 3  # Desviaciones estándar
    
    # Configuración de reportes
    REPORT_FORMATS = ['excel', 'html']
    DEFAULT_REPORT_FORMAT = 'excel'
    
    # Columnas comunes en datasets de ventas
    COMMON_SALES_COLS = {
        'sales': ['ventas', 'sales', 'vendas', 'cajas vend', 'unidades vendidas'],
        'product': ['producto', 'product', 'produto', 'item', 'sku'],
        'category': ['categoria', 'category', 'rubro', 'departamento', 'laboratorio'],
        'stock': ['stock', 'inventario', 'cajas stock', 'inventory'],
        'price': ['precio', 'price', 'costo', 'pvp']
    }
    
    # Configuración de visualizaciones
    VISUALIZATION_CONFIG = {
        'default_style': 'seaborn',
        'figure_size': (12, 8),
        'color_palette': 'viridis'
    }