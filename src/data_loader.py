import pandas as pd
import numpy as np
import chardet
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
from config.settings import AnalysisConfig

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Carga inteligente y validación de datasets"""
    
    def __init__(self):
        self.df = None
        self.metadata = {}
        self.config = AnalysisConfig()
    
    def detect_encoding(self, file_path: str) -> str:
        """Detecta la codificación del archivo"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Leer solo los primeros 10KB para eficiencia
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or self.config.DEFAULT_ENCODING
                logger.info(f"Codificación detectada: {encoding} (confianza: {result['confidence']:.2f})")
                return encoding
        except Exception as e:
            logger.warning(f"No se pudo detectar codificación, usando default: {e}")
            return self.config.DEFAULT_ENCODING
    
    def detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Detecta el delimitador del CSV"""
        delimiters = [',', ';', '\t', '|']
        best_delimiter = ','
        max_columns = 0
        
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                first_line = file.readline()
                
            for delimiter in delimiters:
                column_count = len(first_line.split(delimiter))
                if column_count > max_columns and column_count > 1:
                    max_columns = column_count
                    best_delimiter = delimiter
            
            logger.info(f"Delimitador detectado: '{best_delimiter}' ({max_columns} columnas)")
            return best_delimiter
        except Exception as e:
            logger.warning(f"No se pudo detectar delimitador, usando coma: {e}")
            return ','
    
    def validate_file(self, file_path: str) -> bool:
        """Valida el archivo antes de cargarlo"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        if file_path.suffix.lower() not in self.config.SUPPORTED_FORMATS:
            raise ValueError(f"Formato no soportado: {file_path.suffix}. Formatos válidos: {self.config.SUPPORTED_FORMATS}")
        
        # Verificar tamaño del archivo
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.MAX_FILE_SIZE_MB:
            raise ValueError(f"Archivo demasiado grande: {file_size_mb:.2f}MB. Límite: {self.config.MAX_FILE_SIZE_MB}MB")
        
        logger.info(f"Archivo validado: {file_path.name} ({file_size_mb:.2f} MB)")
        return True
    
    def smart_load(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Carga inteligente del dataset con detección automática"""
        try:
            self.validate_file(file_path)
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.csv':
                encoding = self.detect_encoding(file_path)
                delimiter = self.detect_delimiter(file_path, encoding)
                
                # Intentar cargar con diferentes configuraciones
                df = pd.read_csv(
                    file_path, 
                    encoding=encoding,
                    sep=delimiter,
                    engine='python',
                    on_bad_lines='warn',
                    **kwargs
                )
                
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, **kwargs)
            
            else:
                raise ValueError(f"Formato no soportado: {file_path.suffix}")
            
            self.df = self._post_process_dataframe(df)
            self._extract_metadata()
            
            logger.info(f"✅ Dataset cargado exitosamente: {df.shape[0]} filas, {df.shape[1]} columnas")
            return self.df
            
        except Exception as e:
            logger.error(f"❌ Error cargando archivo {file_path}: {e}")
            raise
    
    def _post_process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Post-procesamiento del DataFrame"""
        # Eliminar espacios en nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        
        # Resetear índice
        df = df.reset_index(drop=True)
        
        return df
    
    def _extract_metadata(self):
        """Extrae metadatos detallados del dataset"""
        if self.df is None:
            return
        
        self.metadata = {
            'basic_info': {
                'shape': self.df.shape,
                'columns': list(self.df.columns),
                'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024**2
            },
            'data_types': {
                str(dtype): list(self.df.select_dtypes(include=[dtype]).columns)
                for dtype in self.df.dtypes.unique()
            },
            'missing_data': {
                'total_missing': self.df.isnull().sum().sum(),
                'missing_by_column': self.df.isnull().sum().to_dict(),
                'completeness_percentage': (1 - self.df.isnull().sum().sum() / (self.df.shape[0] * self.df.shape[1])) * 100
            },
            'column_analysis': self._analyze_columns()
        }
    
    def _analyze_columns(self) -> Dict[str, Any]:
        """Análisis detallado por columna"""
        analysis = {}
        
        for col in self.df.columns:
            col_data = self.df[col]
            analysis[col] = {
                'data_type': str(col_data.dtype),
                'unique_values': col_data.nunique(),
                'missing_values': col_data.isnull().sum(),
                'sample_data': col_data.head(3).tolist() if col_data.dtype == 'object' else None
            }
            
            if pd.api.types.is_numeric_dtype(col_data):
                analysis[col].update({
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'mean': col_data.mean(),
                    'median': col_data.median(),
                    'std': col_data.std()
                })
        
        return analysis
    
    def get_column_mapping(self) -> Dict[str, str]:
        """Mapeo inteligente de columnas basado en nombres"""
        mapping = {}
        column_names = [col.lower() for col in self.df.columns]
        
        for standard_name, possible_names in self.config.COMMON_SALES_COLS.items():
            for possible in possible_names:
                matching_cols = [col for col in self.df.columns if possible in col.lower()]
                if matching_cols:
                    mapping[standard_name] = matching_cols[0]
                    break
        
        logger.info(f"Columnas mapeadas: {mapping}")
        return mapping
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen completo del dataset cargado"""
        return {
            'metadata': self.metadata,
            'column_mapping': self.get_column_mapping(),
            'preview': self.df.head(10).to_dict('records') if self.df is not None else None
        }
    # En src/data_loader.py - agregar esta función
def load_farmacia_format(self, file_path: str) -> pd.DataFrame:
    """Carga específica para el formato de Farmacia Magadán"""
    try:
        # Tu CSV usa ; como separador y tiene encoding específico
        df = pd.read_csv(
            file_path, 
            sep=';',
            encoding='latin-1',  # Común en archivos en español
            skiprows=4,  # Saltar filas de metadata si es necesario
            decimal=',',  # Para formato europeo de decimales
            thousands='.'  # Para formato de miles
        )
        
        # Limpieza específica para tu formato
        df = self._clean_farmacia_data(df)
        return df
        
    except Exception as e:
        logger.error(f"Error cargando formato farmacia: {e}")
        # Fallback al método automático
        return self.smart_load(file_path)

def _clean_farmacia_data(self, df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza específica para datos de farmacia"""
    # Eliminar columnas completamente vacías
    df = df.dropna(axis=1, how='all')
    
    # Convertir columnas numéricas (manejar comas como decimales)
    for col in df.columns:
        if df[col].dtype == 'object':
            # Intentar convertir a numérico
            try:
                df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='ignore')
            except:
                pass
    
    return df
# En src/data_loader.py - agregar este método
def load_farmacia_format(self, file_path: str) -> pd.DataFrame:
    """Carga específica para el formato de Farmacia Magadán"""
    try:
        # Tu CSV específico
        df = pd.read_csv(
            file_path, 
            sep=';',
            encoding='utf-8',  # o 'latin-1' si es necesario
            decimal=',',
            thousands='.'
        )
        
        # Limpieza específica
        df = self._clean_farmacia_data(df)
        return df
        
    except Exception as e:
        logger.warning(f"No se pudo cargar con formato farmacia, usando carga automática: {e}")
        return self.smart_load(file_path)

def _clean_farmacia_data(self, df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza específica para datos de farmacia"""
    # Eliminar filas completamente vacías
    df = df.dropna(how='all')
    
    # Eliminar columnas completamente vacías
    df = df.dropna(axis=1, how='all')
    
    # Resetear índice
    df = df.reset_index(drop=True)
    
    return df