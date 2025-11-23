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
    """Función principal para uso por consola"""
    print("🚀 ANALYTICS SUITE - Sistema de Análisis (Modo Consola)")
    print("=" * 60)
    print("💡 Para el dashboard web, ejecuta: streamlit run app.py")
    print("=" * 60)
    
    # Buscar archivos CSV
    csv_files = list(Path('.').glob('*.csv'))
    if not csv_files:
        csv_files = list(Path('data').glob('*.csv'))
    
    if not csv_files:
        print("❌ No se encontraron archivos CSV")
        return
    
    print("📁 Archivos CSV encontrados:")
    for i, file in enumerate(csv_files, 1):
        print(f"   {i}. {file}")
    
    try:
        selection = input("\nSelecciona el número del archivo a analizar: ")
        selected_file = csv_files[int(selection) - 1]
    except (ValueError, IndexError):
        print("❌ Selección inválida")
        return
    
    print(f"\n📊 Analizando: {selected_file}")
    print("-" * 50)
    
    # Cargar y analizar datos
    loader = DataLoader()
    try:
        df = loader.smart_load(str(selected_file))
        print(f"✅ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        # Análisis
        analyzer = DataAnalyzer(df)
        analysis = analyzer.comprehensive_analysis()
        
        # Resultados
        print(f"\n📈 RESULTADOS:")
        print(f"   - Total registros: {analysis['basic_stats']['total_rows']}")
        print(f"   - Columnas: {analysis['basic_stats']['total_columns']}")
        
        # Productos con stock bajo
        low_stock = analyzer._identify_low_stock()
        print(f"   - Productos con stock bajo: {len(low_stock)}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        for rec in analysis.get('recommendations', []):
            print(f"   • {rec}")
        
        # Generar reporte
        print(f"\n💾 Generando reporte...")
        reporter = ReportGenerator()
        report_path = reporter.generate_comprehensive_report(df, analysis)
        print(f"   ✅ Reporte guardado: {report_path}")
        
        print(f"\n🎉 ANÁLISIS COMPLETADO!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()