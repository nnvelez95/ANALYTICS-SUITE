import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Análisis avanzado de datos de ventas"""
    
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.column_mapping = {}
    
    def comprehensive_analysis(self) -> Dict[str, Any]:
        """Análisis completo del dataset"""
        analysis = {}
        
        analysis['basic_stats'] = self._get_basic_statistics()
        analysis['sales_analysis'] = self._analyze_sales()
        analysis['inventory_analysis'] = self._analyze_inventory()
        analysis['trends'] = self._detect_trends()
        analysis['anomalies'] = self._detect_anomalies()
        analysis['recommendations'] = self._generate_recommendations()
        
        return analysis
    
    def _get_basic_statistics(self) -> Dict:
        """Estadísticas básicas del dataset"""
        stats = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024**2,
            'missing_values': self.df.isnull().sum().sum(),
            'duplicate_rows': self.df.duplicated().sum()
        }
        
        # Estadísticas por tipo de dato
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        stats['numeric_columns'] = len(numeric_cols)
        stats['categorical_columns'] = len(self.df.select_dtypes(include=['object']).columns)
        
        return stats
    
    def _analyze_sales(self) -> Dict:
        """Análisis detallado de ventas"""
        sales_cols = [col for col in self.df.columns if 'vent' in col.lower() or 'sales' in col.lower()]
        
        if not sales_cols:
            return {'error': 'No se encontraron columnas de ventas'}
        
        sales_analysis = {}
        
        for col in sales_cols:
            if self.df[col].dtype in [np.int64, np.float64]:
                sales_data = self.df[col]
                sales_analysis[col] = {
                    'total': sales_data.sum(),
                    'mean': sales_data.mean(),
                    'median': sales_data.median(),
                    'std': sales_data.std(),
                    'max': sales_data.max(),
                    'min': sales_data.min(),
                    'zero_sales': (sales_data == 0).sum(),
                    'top_products': self._get_top_products(sales_data)
                }
        
        return sales_analysis
    
    def _analyze_inventory(self) -> Dict:
        """Análisis de inventario y stock"""
        stock_cols = [col for col in self.df.columns if 'stock' in col.lower()]
        
        inventory_analysis = {
            'low_stock_items': self._identify_low_stock(),
            'overstock_items': self._identify_overstock(),
            'stock_turnover': self._calculate_turnover(),
            'abc_analysis': self._perform_abc_analysis()
        }
        
        return inventory_analysis
    
    def _identify_low_stock(self, threshold: int = 5) -> pd.DataFrame:
        """Identifica productos con stock bajo"""
        stock_cols = [col for col in self.df.columns if 'stock' in col.lower()]
        
        if not stock_cols:
            return pd.DataFrame()
        
        low_stock_mask = (self.df[stock_cols[0]] <= threshold) & (self.df[stock_cols[0]] >= 0)
        return self.df[low_stock_mask].sort_values(stock_cols[0])
    
    def _detect_anomalies(self) -> Dict:
        """Detección de anomalías usando métodos estadísticos"""
        anomalies = {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Método Z-score
            z_scores = np.abs(stats.zscore(self.df[col].dropna()))
            anomalies_z = self.df[z_scores > 3]
            
            # Método IQR
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            anomalies_iqr = self.df[(self.df[col] < (Q1 - 1.5 * IQR)) | (self.df[col] > (Q3 + 1.5 * IQR))]
            
            anomalies[col] = {
                'z_score_anomalies': len(anomalies_z),
                'iqr_anomalies': len(anomalies_iqr),
                'samples': anomalies_iqr.head().to_dict('records')
            }
        
        return anomalies
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        # Análisis de stock
        low_stock = self._identify_low_stock()
        if len(low_stock) > 0:
            recommendations.append(f"🚨 {len(low_stock)} productos necesitan reposición urgente")
        
        # Análisis de ventas
        sales_cols = [col for col in self.df.columns if 'vent' in col.lower()]
        if sales_cols:
            zero_sales = (self.df[sales_cols[0]] == 0).sum()
            if zero_sales > len(self.df) * 0.3:  # Más del 30% sin ventas
                recommendations.append(f"📊 {zero_sales} productos sin ventas - considerar rotación")
        
        # Análisis de datos faltantes
        missing_total = self.df.isnull().sum().sum()
        if missing_total > 0:
            recommendations.append(f"⚠️  {missing_total} valores faltantes detectados")
        
        return recommendations
    # En src/data_analyzer.py - agregar estas funciones
def analyze_farmacia_specific(self) -> Dict[str, Any]:
    """Análisis específico para datos de farmacia"""
    analysis = {}
    
    analysis['laboratorio_analysis'] = self._analyze_by_laboratorio()
    analysis['rubro_analysis'] = self._analyze_by_rubro() 
    analysis['price_margin_analysis'] = self._analyze_price_margins()
    analysis['rotation_analysis'] = self._analyze_product_rotation()
    
    return analysis

def _analyze_by_laboratorio(self) -> Dict:
    """Análisis de ventas y stock por laboratorio"""
    lab_col = self._find_column(['laboratorio', 'lab', 'fabricante'])
    sales_col = self._find_column(['cajas vend. total', 'ventas total'])
    
    if lab_col and sales_col:
        lab_analysis = self.df.groupby(lab_col).agg({
            sales_col: ['sum', 'count', 'mean'],
            self._find_column(['cajas stock total']): 'sum'
        }).round(2)
        
        return lab_analysis.sort_values((sales_col, 'sum'), ascending=False)
    return {}

def _analyze_product_rotation(self) -> pd.DataFrame:
    """Calcula rotación de productos (ventas/stock)"""
    sales_col = self._find_column(['cajas vend. total'])
    stock_col = self._find_column(['cajas stock total'])
    
    if sales_col and stock_col:
        df_rotation = self.df.copy()
        df_rotation['rotacion'] = df_rotation[sales_col] / df_rotation[stock_col].replace(0, 1)
        df_rotation['estado_rotacion'] = pd.cut(
            df_rotation['rotacion'], 
            bins=[-1, 0.1, 0.5, 1, 5, float('inf')],
            labels=['Sin ventas', 'Baja', 'Media', 'Alta', 'Muy Alta']
        )
        
        return df_rotation[['Producto', 'Laboratorio', sales_col, stock_col, 'rotacion', 'estado_rotacion']]
    return pd.DataFrame()