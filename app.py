import gradio as gr
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tempfile
import subprocess
import os
from rpy2.robjects import r, pandas2ri

pandas2ri.activate()

# Función principal
def eda_interface(file, show_info, show_plot, plot_type, eda_python, eda_r):
    output = ""
    df = None

    if file is not None:
        df = pd.read_csv(file.name)
    else:
        return "Por favor suba un archivo CSV", None, None, None

    # Mostrar info
    if show_info:
        output += "### DataFrame Info\n"
        buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        df.info(buf=buffer)
        buffer.close()
        with open(buffer.name, "r") as f:
            output += f.read()
        os.remove(buffer.name)

        output += "\n\n### DataFrame Describe (Transpuesta)\n"
        output += df.describe().T.to_markdown()

        # Pairplot (Seaborn)
        sns_plot = sns.pairplot(df.select_dtypes("number"))
        sns_fig = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        sns_plot.savefig(sns_fig.name)
        sns_plot_fig_path = sns_fig.name
    else:
        sns_plot_fig_path = None

    # Mostrar gráfico seleccionado
    graph_path = None
    if show_plot:
        fig, ax = plt.subplots()
        if plot_type == "histograma":
            df.select_dtypes("number").hist(ax=ax)
        elif plot_type == "barras":
            df.select_dtypes("object").iloc[:, 0].value_counts().plot(kind='bar', ax=ax)
        elif plot_type == "pie":
            df.select_dtypes("object").iloc[:, 0].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
        elif plot_type == "puntos":
            numeric = df.select_dtypes("number")
            if numeric.shape[1] >= 2:
                ax.scatter(numeric.iloc[:, 0], numeric.iloc[:, 1])
        graph_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        plt.savefig(graph_path)
        plt.close()

    # Generar reporte EDA en Python
    report_python = None
    if eda_python:
        report_python = tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name
        with open(report_python, "w") as f:
            f.write("Reporte EDA en Python\n")
            f.write(df.describe(include='all').to_string())
    
    # Generar reporte EDA en R
    report_r = None
    if eda_r:
        r.assign("df_r", pandas2ri.py2rpy(df))
        report_r = tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name
        r(f"""
        sink("{report_r}")
        summary(df_r)
        sink()
        """)

    return output, sns_plot_fig_path, graph_path, report_python, report_r

# Interfaz Gradio
iface = gr.Interface(
    fn=eda_interface,
    inputs=[
        gr.File(label="Sube un archivo CSV"),
        gr.Checkbox(label="Mostrar info del DataFrame"),
        gr.Checkbox(label="Mostrar gráfico"),
        gr.Dropdown(choices=["histograma", "barras", "pie", "puntos"], label="Tipo de gráfico"),
        gr.Checkbox(label="Generar reporte EDA en Python"),
        gr.Checkbox(label="Generar reporte EDA en R")
    ],
    outputs=[
        gr.Textbox(label="Información del DataFrame"),
        gr.Image(label="Pairplot (Seaborn)", type="filepath"),
        gr.Image(label="Gráfico personalizado", type="filepath"),
        gr.File(label="Reporte Python"),
        gr.File(label="Reporte R")
    ],
    title="Análisis Exploratorio de Datos (EDA) con Python + R"
)

if __name__ == "__main__":
    iface.launch()
