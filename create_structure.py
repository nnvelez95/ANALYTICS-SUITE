import os
from pathlib import Path

def create_project_structure():
    """Crea la estructura completa de carpetas del proyecto"""
    
    # Directorios principales
    directories = [
        'src',
        'config', 
        'outputs/reports',
        'outputs/plots',
        'tests',
        'data'
    ]
    
    # Archivos de configuración
    config_files = {
        'config/__init__.py': '',
        'config/settings.py': '''
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
''',
        
        'src/__init__.py': '',
        'tests/__init__.py': '',
        'outputs/.gitkeep': '',
        'data/.gitkeep': '',
        
        'requirements.txt': '''
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0
openpyxl>=3.1.0
streamlit>=1.24.0
scipy>=1.10.0
scikit-learn>=1.2.0
chardet>=5.1.0
python-dateutil>=2.8.2
'''
    }
    
    print("🚀 Creando estructura del proyecto...")
    
    # Crear directorios
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Carpeta creada: {directory}")
    
    # Crear archivos de configuración
    for file_path, content in config_files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✅ Archivo creado: {file_path}")
    
    print("\\n🎯 Estructura del proyecto creada exitosamente!")
    print("\\n📁 Estructura final:")
    print("analytics_suite/")
    print("├── src/")
    print("├── config/")
    print("│   └── settings.py")
    print("├── outputs/")
    print("│   ├── reports/")
    print("│   └── plots/")
    print("├── tests/")
    print("├── data/")
    print("└── requirements.txt")

if __name__ == "__main__":
    create_project_structure()