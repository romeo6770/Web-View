import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer
from scipy import stats

# Función para cargar datos desde diferentes fuentes
def cargar_datos(ruta_archivo, tipo='csv', **kwargs):
    """
    Carga datos desde diferentes tipos de archivos.
    
    Args:
        ruta_archivo: Ruta del archivo a cargar
        tipo: Tipo de archivo (csv, excel, json)
        **kwargs: Argumentos adicionales para la función de carga
        
    Returns:
        DataFrame de pandas con los datos cargados
    """
    if tipo.lower() == 'csv':
        return pd.read_csv(ruta_archivo, **kwargs)
    elif tipo.lower() == 'excel':
        return pd.read_excel(ruta_archivo, **kwargs)
    elif tipo.lower() == 'json':
        return pd.read_json(ruta_archivo, **kwargs)
    else:
        raise ValueError(f"Tipo de archivo {tipo} no soportado")

# Funciones para limpieza de datos
def limpiar_datos(df, columnas_a_limpiar=None):
    """
    Limpia un conjunto de datos eliminando o imputando valores nulos.
    
    Args:
        df: DataFrame a limpiar
        columnas_a_limpiar: Lista de columnas a limpiar (None para todas)
        
    Returns:
        DataFrame limpio
    """
    if columnas_a_limpiar is None:
        columnas_a_limpiar = df.columns
        
    # Crear una copia para no modificar el original
    df_limpio = df.copy()
    
    # Eliminar filas con todos los valores nulos
    df_limpio = df_limpio.dropna(how='all')
    
    return df_limpio

def imputar_valores(df, estrategia='media', columnas=None):
    """
    Imputa valores faltantes usando diferentes estrategias.
    
    Args:
        df: DataFrame con valores a imputar
        estrategia: Estrategia de imputación ('media', 'mediana', 'moda')
        columnas: Columnas a imputar (None para todas las numéricas)
        
    Returns:
        DataFrame con valores imputados
    """
    df_imputado = df.copy()
    
    if columnas is None:
        columnas = df.select_dtypes(include=[np.number]).columns
    
    imputer = SimpleImputer(strategy=estrategia)
    df_imputado[columnas] = imputer.fit_transform(df_imputado[columnas])
    
    return df_imputado

# Funciones para transformación de datos
def normalizar_datos(df, columnas=None, metodo='minmax'):
    """
    Normaliza los datos numéricos en un rango específico.
    
    Args:
        df: DataFrame a normalizar
        columnas: Lista de columnas a normalizar (None para todas las numéricas)
        metodo: Método de normalización ('minmax', 'zscore')
        
    Returns:
        DataFrame normalizado
    """
    df_norm = df.copy()
    
    if columnas is None:
        columnas = df.select_dtypes(include=[np.number]).columns
    
    if metodo == 'minmax':
        scaler = MinMaxScaler()
        df_norm[columnas] = scaler.fit_transform(df_norm[columnas])
    elif metodo == 'zscore':
        scaler = StandardScaler()
        df_norm[columnas] = scaler.fit_transform(df_norm[columnas])
    
    return df_norm

# Funciones para agregación y estadísticas
def agrupar_datos(df, columnas_agrupacion, columnas_valor, funcion='mean'):
    """
    Agrupa datos por las columnas especificadas y aplica una función a las columnas de valor.
    
    Args:
        df: DataFrame a agrupar
        columnas_agrupacion: Columnas por las cuales agrupar
        columnas_valor: Columnas a las que aplicar la función
        funcion: Función a aplicar ('mean', 'sum', 'count', etc.)
        
    Returns:
        DataFrame agrupado
    """
    return df.groupby(columnas_agrupacion)[columnas_valor].agg(funcion).reset_index()

def calcular_estadisticas(df, columnas=None):
    """
    Calcula estadísticas descriptivas para las columnas especificadas.
    
    Args:
        df: DataFrame para calcular estadísticas
        columnas: Columnas a analizar (None para todas las numéricas)
        
    Returns:
        DataFrame con estadísticas descriptivas
    """
    if columnas is None:
        columnas = df.select_dtypes(include=[np.number]).columns
        
    return df[columnas].describe()

# Función para detectar outliers
def detectar_outliers(df, columna, metodo='iqr'):
    """
    Detecta outliers en una columna específica.
    
    Args:
        df: DataFrame a analizar
        columna: Nombre de la columna a analizar
        metodo: Método para detectar outliers ('iqr', 'zscore')
        
    Returns:
        Índices de las filas con outliers
    """
    if metodo == 'iqr':
        Q1 = df[columna].quantile(0.25)
        Q3 = df[columna].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[columna] < lower_bound) | (df[columna] > upper_bound)].index
        
    elif metodo == 'zscore':
        z_scores = np.abs(stats.zscore(df[columna]))
        outliers = df[z_scores > 3].index
        
    return outliers