import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 2. Crear o conectar a la base de datos SQLite en el mismo environment
#    Esto crea un archivo 'traffic_analysis.db' en el directorio actual
conn = sqlite3.connect('traffic_analysis.db')
cursor = conn.cursor()

# 3. Leer archivos CSV (omitimos líneas de comentario que empiezan con '#')
audiences_df       = pd.read_csv('audiences.csv', comment='#')
demographics_df    = pd.read_csv('demographics.csv', comment='#')
engagement_df      = pd.read_csv('engagement.csv', comment='#')
pages_df           = pd.read_csv('pages.csv', comment='#')
reports_df         = pd.read_csv('reports.csv', comment='#')
tech_details_df    = pd.read_csv('tech_details.csv', comment='#')
tech_overview_df   = pd.read_csv('tech_overview.csv', comment='#')
user_acquisition_df= pd.read_csv('user_acquisition.csv', comment='#')

# 4. Guardar DataFrames como tablas en la base de datos SQLite
audiences_df.to_sql('audiences',       conn, if_exists='replace', index=False)
demographics_df.to_sql('demographics',   conn, if_exists='replace', index=False)
engagement_df.to_sql('engagement',       conn, if_exists='replace', index=False)
pages_df.to_sql('pages',                 conn, if_exists='replace', index=False)
reports_df.to_sql('reports',             conn, if_exists='replace', index=False)
tech_details_df.to_sql('tech_details',   conn, if_exists='replace', index=False)
tech_overview_df.to_sql('tech_overview', conn, if_exists='replace', index=False)
user_acquisition_df.to_sql('user_acquisition', conn, if_exists='replace', index=False)
conn.commit()

# 5. (Opcional) Volver a cargar las tablas desde SQLite para verificar integridad
#    y trabajar con ellas en downstream
table_names = ['audiences', 'demographics', 'engagement', 'pages',
               'reports', 'tech_details', 'tech_overview', 'user_acquisition']

dfs = {}
for table in table_names:
    dfn = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    dfs[f"{table}_df"] = dfn
    print(f"Tabla '{table}' cargada: {dfn.shape[0]} filas x {dfn.shape[1]} columnas")

# 6. Asignar variables finales para uso en análisis posterior
audiences_df       = dfs['audiences_df']
demographics_df    = dfs['demographics_df']
engagement_df      = dfs['engagement_df']
pages_df           = dfs['pages_df']
reports_df         = dfs['reports_df']
tech_details_df    = dfs['tech_details_df']
tech_overview_df   = dfs['tech_overview_df']
user_acquisition_df= dfs['user_acquisition_df']

print("Audiences:")
print(audiences_df.head())

print("Demographics:")
print(demographics_df.head())

print("Engagement Overview:")
print(engagement_df.head())

#7- convierte columnas
def convert_numeric(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

#convierte columnas a DataFrame de Audiences
audiences_df = convert_numeric(audiences_df, ["Total users", "New users", "Sessions", "Views per session", "Average session duration", "Total revenue"])

#convierte columnas a DataFrame de Audiences
demographics_df = convert_numeric(demographics_df, ["Active users", "New users", "Engaged sessions", "Event count", "Total revenue"])

#8- Crea gráficas

# Gráfica 1: Total users vs New users

if audiences_df is not None and not audiences_df.empty:
    audiences_melt = audiences_df.melt(id_vars=["Audience name"],
                                         value_vars=["Total users", "New users"],
                                         var_name="Tipo", value_name="Usuarios")
    plt.figure()
    sns.barplot(x="Audience name", y="Usuarios", hue="Tipo", data=audiences_melt)
    plt.title("Usuarios Totales vs Nuevos en Audiences")
    plt.xlabel("Nombre de la Audiencia")
    plt.ylabel("Cantidad de Usuarios")
    plt.legend(title="Tipo")
    plt.show()

# Gráfica 2: Usuarios activos por localidad
if demographics_df is not None and not demographics_df.empty:
    plt.figure()
    sns.barplot(x="Country", y="Active users", data=demographics_df)
    plt.title("Usuarios Activos por País")
    plt.xlabel("País")
    plt.ylabel("Usuarios Activos")
    plt.show()

# Gráfica 3: Average engagement time per active user
if engagement_df is not None and not engagement_df.empty and "Nth day" in engagement_df.columns:
    engagement_df = convert_numeric(engagement_df, ["Nth day", "Average engagement time per active user"])
    plt.figure()
    sns.lineplot(x="Nth day", y="Average engagement time per active user", data=engagement_df, marker="o")
    plt.title("Tendencia de Tiempo Promedio de Engagement")
    plt.xlabel("Nth day")
    plt.ylabel("Tiempo de Engagement (segundos)")
    plt.show()

# Gráfica 4: Distribución de usuarios activos por plataforma
if tech_overview_df is not None and not tech_overview_df.empty:
    tech_overview_df = convert_numeric(tech_overview_df, ["Active users"])
    plt.figure()
    sns.barplot(x="Platform", y="Active users", data=tech_overview_df)
    plt.title("Usuarios Activos por Plataforma")
    plt.xlabel("Plataforma")
    plt.ylabel("Usuarios Activos")
    plt.show()

    #5- Crea relaciones de datos

#relación 1: Distribución de Canales de Adquisición de Usuarios
if user_acquisition_df is not None and not user_acquisition_df.empty:
    acquisition = user_acquisition_df.groupby("First user primary channel group (Default Channel Group)")["Total users"].sum().reset_index()
    plt.figure()
    plt.pie(acquisition["Total users"], labels=acquisition["First user primary channel group (Default Channel Group)"], autopct='%1.1f%%', startangle=140)
    plt.title("Distribución de Canales de Adquisición de Usuarios")
    plt.show()

#relación 2: Usuarios Activos por Categoría de Dispositivo
if tech_overview_df is not None and not tech_overview_df.empty and "Platform / device category" in tech_overview_df.columns:
    plt.figure()
    sns.barplot(x="Platform / device category", y="Active users", data=tech_overview_df)
    plt.title("Usuarios Activos por Categoría de Dispositivo")
    plt.xlabel("Categoría de Dispositivo")
    plt.ylabel("Usuarios Activos")
    plt.show()

#relación 3: Usuarios Activos por Navegador
if tech_details_df is not None and not tech_details_df.empty:
    plt.figure()
    sns.barplot(x="Browser", y="Active users", data=tech_details_df)
    plt.title("Usuarios Activos por Navegador")
    plt.xlabel("Navegador")
    plt.ylabel("Usuarios Activos")
    plt.show()

#relación 4: Engagement por región
if demographics_df is not None and not demographics_df.empty:
    if "Engaged sessions" in demographics_df.columns and "Active users" in demographics_df.columns:
        demographics_df["Engagement Ratio"] = demographics_df["Engaged sessions"] / demographics_df["Active users"]
        plt.figure()
        sns.barplot(x="Country", y="Engagement Ratio", data=demographics_df)
        plt.title("Ratio de Engagement por País")
        plt.xlabel("País")
        plt.ylabel("Ratio de Engagement")
        plt.show()