import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sns.set_theme(style="whitegrid", palette="muted", font_scale=0.8)

# Configuración de la figura
FIGSIZE = (2.5, 2.5)

# Función para convertir columnas a numéricas
def convert_numeric(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# Función para cargar datos desde SQLite
def load_data():
    conn = sqlite3.connect('traffic_analysis.db')
    tables = ['audiences', 'demographics', 'engagement', 'pages',
              'reports', 'tech_details', 'tech_overview', 'user_acquisition']
    data = {tbl: pd.read_sql_query(f"SELECT * FROM {tbl}", conn) for tbl in tables}
    conn.close()
    return data

# Cargar y preprocesar dataframes
dfs = load_data()
audiences_df = convert_numeric(dfs['audiences'], ["Total users", "New users", "Sessions", "Views per session", "Average session duration", "Total revenue"])
demographics_df = convert_numeric(dfs['demographics'], ["Active users", "New users", "Engaged sessions", "Event count", "Total revenue"])
engagement_df = dfs['engagement'].copy()
tech_details_df = convert_numeric(dfs['tech_details'], ["Active users"])
tech_overview_df = convert_numeric(dfs['tech_overview'], ["Active users"])
user_acquisition_df = convert_numeric(dfs['user_acquisition'], ["Total users"])

# Funciones de creación de gráficas (devuelven None si no jala)
def plot_audiences_bar():
    if audiences_df.empty: return None
    fig, ax = plt.subplots(figsize=FIGSIZE)
    melt = audiences_df.melt(id_vars=["Audience name"], value_vars=["Total users", "New users"], var_name="Tipo", value_name="Usuarios")
    sns.barplot(x="Audience name", y="Usuarios", hue="Tipo", data=melt, ax=ax)
    ax.set_title("Usuarios Totales vs Nuevos", fontsize=10)
    ax.set_xlabel("Audiencia", fontsize=8)
    ax.set_ylabel("Usuarios", fontsize=8)
    ax.tick_params(axis='x', rotation=45, labelsize=6)
    ax.tick_params(axis='y', labelsize=6)
    ax.legend(title="Tipo", fontsize=6, title_fontsize=7)
    fig.tight_layout(pad=1)
    return fig


def plot_active_by_country():
    if demographics_df.empty or "Country" not in demographics_df.columns: return None
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sns.barplot(x="Country", y="Active users", data=demographics_df, ax=ax)
    ax.set_title("Usuarios Activos por País", fontsize=10)
    ax.set_xlabel("País", fontsize=8)
    ax.set_ylabel("Activos", fontsize=8)
    ax.tick_params(axis='x', rotation=45, labelsize=6)
    ax.tick_params(axis='y', labelsize=6)
    fig.tight_layout(pad=1)
    return fig


def plot_engagement_trend():
    if engagement_df.empty or "Nth day" not in engagement_df.columns: return None
    df = convert_numeric(engagement_df, ["Nth day", "Average engagement time per active user"])
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sns.lineplot(x="Nth day", y="Average engagement time per active user", data=df, marker="o", ax=ax)
    ax.set_title("Tendencia de Engagement", fontsize=10)
    ax.set_xlabel("Día (Nth)", fontsize=8)
    ax.set_ylabel("Engagement (s)", fontsize=8)
    ax.tick_params(labelsize=6)
    fig.tight_layout(pad=1)
    return fig


def plot_platform_active():
    if tech_overview_df.empty or "Platform" not in tech_overview_df.columns: return None
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sns.barplot(x="Platform", y="Active users", data=tech_overview_df, ax=ax)
    ax.set_title("Activos por Plataforma", fontsize=10)
    ax.set_xlabel("Plataforma", fontsize=8)
    ax.set_ylabel("Activos", fontsize=8)
    ax.tick_params(axis='x', rotation=45, labelsize=6)
    ax.tick_params(axis='y', labelsize=6)
    fig.tight_layout(pad=1)
    return fig


def plot_acquisition_pie():
    if user_acquisition_df.empty or "First user primary channel group (Default Channel Group)" not in user_acquisition_df.columns: return None
    fig, ax = plt.subplots(figsize=FIGSIZE)
    acq = user_acquisition_df.groupby(
        "First user primary channel group (Default Channel Group)"
    )["Total users"].sum().reset_index()
    ax.pie(acq["Total users"], labels=acq["First user primary channel group (Default Channel Group)"], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 6})
    ax.set_title("Canales de Adquisición", fontsize=10)
    fig.tight_layout(pad=1)
    return fig


def plot_device_category():
    col = next((c for c in tech_overview_df.columns if "device" in c.lower()), None)
    if tech_overview_df.empty or not col: return None
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sns.barplot(x=col, y="Active users", data=tech_overview_df, ax=ax)
    ax.set_title("Activos por Dispositivo", fontsize=10)
    ax.set_xlabel(col, fontsize=8)
    ax.set_ylabel("Activos", fontsize=8)
    ax.tick_params(axis='x', rotation=45, labelsize=6)
    ax.tick_params(axis='y', labelsize=6)
    fig.tight_layout(pad=1)
    return fig


def plot_browser_active():
    if tech_details_df.empty or "Browser" not in tech_details_df.columns: return None
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sns.barplot(x="Browser", y="Active users", data=tech_details_df, ax=ax)
    ax.set_title("Activos por Navegador", fontsize=10)
    ax.set_xlabel("Navegador", fontsize=8)
    ax.set_ylabel("Activos", fontsize=8)
    ax.tick_params(axis='x', rotation=45, labelsize=6)
    ax.tick_params(axis='y', labelsize=6)
    fig.tight_layout(pad=1)
    plt.savefig('browser.png', bbox_inches='tight')
    return fig


def plot_engagement_ratio():
    if demographics_df.empty or "Engaged sessions" not in demographics_df.columns: return None
    df = demographics_df.copy()
    df["Ratio"] = df["Engaged sessions"] / df["Active users"].replace(0, pd.NA)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sns.barplot(x="Country", y="Ratio", data=df, ax=ax)
    ax.set_title("Ratio Engagement por País", fontsize=10)
    ax.set_xlabel("País", fontsize=8)
    ax.set_ylabel("Ratio", fontsize=8)
    ax.tick_params(axis='x', rotation=45, labelsize=6)
    ax.tick_params(axis='y', labelsize=6)
    fig.tight_layout(pad=1)
    return fig

# Lista de funciones para gráficas
templates = [
    plot_audiences_bar,
    plot_active_by_country,
    plot_engagement_trend,
    plot_platform_active,
    plot_acquisition_pie,
    plot_device_category,
    plot_browser_active,
    plot_engagement_ratio
]

# Se crea interfaz gráfica con tkinter
root = tk.Tk()
root.title("Dashboard de Análisis de Tráfico")
root.geometry("1400x900")  # ventana más grande

# Estilos de tkinter
style = ttk.Style()
style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
style.configure("Card.TFrame", background="white", borderwidth=1, relief="solid", padding=5)

# Encabezado sticky
dashboard_header = ttk.Label(root, text="Dashboard de Análisis de Tráfico", style="Header.TLabel")
dashboard_header.pack(pady=(10, 5))

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
canvas = tk.Canvas(main_frame, background="#f0f0f0")
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
plots_frame = ttk.Frame(canvas)
canvas.create_window((0,0), window=plots_frame, anchor="nw")

# Configuración del grid
for col in range(3):
    plots_frame.columnconfigure(col, weight=1)
for row in range(3):
    plots_frame.rowconfigure(row, weight=1)

# Se ponen las gráficas en el grid
valid_figs = [fn() for fn in templates if fn()]
for idx, fig in enumerate(valid_figs[:9]):
    row, col = divmod(idx, 3)
    card = ttk.Frame(plots_frame, style="Card.TFrame")
    card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
    canvas_fig = FigureCanvasTkAgg(fig, master=card)
    widget = canvas_fig.get_tk_widget()
    widget.pack(fill=tk.BOTH, expand=True)

root.mainloop()
