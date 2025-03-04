import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openpyxl


# Clase principal de la aplicación HLIAnalysisApp
class HLIAnalysisApp:
    # constructor de la clase
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Índice de Carga Calórica (HLI)")
        self.root.geometry("800x600")

        # Generar datos
        self.generar_datos()

        # Crear interfaz
        self.crear_interfaz()

    def generar_datos(self):
        """Genera datos simulados para el análisis de HLI"""
        np.random.seed(42)
        n_dias = 180

        # Simulación de datos
        temperatura_ambiente = np.random.uniform(25, 35, n_dias)
        humedad_relativa = np.random.uniform(60, 90, n_dias)
        velocidad_viento = np.random.uniform(0.5, 5, n_dias)
        radiacion_solar = np.random.uniform(200, 800, n_dias)

        # Calcular Temperatura de Globo Negro (BG)
        bg = (
            temperatura_ambiente
            + 0.5 * (radiacion_solar * 0.25)
            - 0.5 * velocidad_viento
        )

        # Crear DataFrame
        self.datos = pd.DataFrame(
            {
                "Dia": range(1, n_dias + 1),
                "Temperatura_Ambiente": temperatura_ambiente,
                "Humedad_Relativa": humedad_relativa,
                "Velocidad_Viento": velocidad_viento,
                "Radiacion_Solar": radiacion_solar,
                "BG": bg,
            }
        )

        # Calcular HLI
        self.datos["HLI"] = self.datos.apply(
            lambda row: self.calcular_hli(
                row["BG"], row["Humedad_Relativa"], row["Velocidad_Viento"]
            ),
            axis=1,
        )

        # Clasificación de riesgo
        self.datos["Riesgo"] = self.datos["HLI"].apply(self.clasificar_riesgo)

    def calcular_hli(self, bg, rh, ws):
        """Calcula el Índice de Carga Calórica (HLI)"""
        if bg > 25:
            hli = 8.62 + (0.38 * rh) + (1.55 * bg) - (0.5 * ws) + np.exp(2.4 - ws)
        else:
            hli = 10.66 + (0.28 * rh) + (1.3 * bg) - ws
        return hli

    def clasificar_riesgo(self, hli):
        """Clasifica el nivel de riesgo según el HLI"""
        if hli < 92:
            return "Sin riesgo"
        elif 92 <= hli < 102:
            return "Riesgo leve"
        elif 102 <= hli < 108:
            return "Riesgo moderado"
        elif 108 <= hli < 113:
            return "Riesgo alto"
        else:
            return "Riesgo extremo"

    def crear_interfaz(self):
        """Crea la interfaz de usuario de Tkinter"""
        # Frame para botones
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)

        # Botones para visualizaciones
        botones = [
            ("HLI por Día", self.mostrar_hli_linea),
            ("Temp vs HLI", self.mostrar_scatter_temp_hli),
            ("Distribución de Riesgo", self.mostrar_distribucion_riesgo),
            ("Exportar a Excel", self.exportar_excel),
            ("Importar desde Excel", self.importar_datos_excel),
        ]

        for texto, comando in botones:
            tk.Button(frame_botones, text=texto, command=comando).pack(
                side=tk.LEFT, padx=5
            )

        # Frame para mostrar gráficos
        self.frame_grafico = tk.Frame(self.root)
        self.frame_grafico.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def mostrar_hli_linea(self):
        """Muestra gráfico de línea de HLI"""
        self.limpiar_frame()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(
            self.datos["Dia"], self.datos["HLI"], label="HLI", color="blue", linewidth=2
        )
        ax.axhline(y=92, color="red", linestyle="--", label="Umbral de estrés leve")
        ax.axhline(
            y=102, color="orange", linestyle="--", label="Umbral de estrés moderado"
        )
        ax.set_title("Variación del Índice de Carga Calórica (HLI)")
        ax.set_xlabel("Día")
        ax.set_ylabel("HLI")
        ax.legend()
        ax.grid(alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH)
        canvas.draw()

    def mostrar_scatter_temp_hli(self):
        """Muestra gráfico de dispersión entre temperatura y HLI"""
        self.limpiar_frame()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(
            self.datos["Temperatura_Ambiente"],
            self.datos["HLI"],
            color="green",
            alpha=0.7,
        )
        ax.set_title("Relación entre Temperatura Ambiente y HLI")
        ax.set_xlabel("Temperatura Ambiente (°C)")
        ax.set_ylabel("HLI")

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH)
        canvas.draw()

    def mostrar_distribucion_riesgo(self):
        """Muestra distribución de días por nivel de riesgo"""
        self.limpiar_frame()

        riego_counts = self.datos["Riesgo"].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ["green", "blue", "orange", "red", "purple"]
        riego_counts.plot(kind="bar", ax=ax, color=colors[: len(riego_counts)])

        ax.set_title("Distribución de días según nivel de riesgo")

        ax.set_xlabel("Nivel de riesgo")
        ax.set_ylabel("Número de días")

        plt.xticks(rotation=45, ha="right")

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)

        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH)
        canvas.draw()

    def exportar_excel(self):
        """Exporta los datos a un archivo Excel"""
        try:
            # Abrir diálogo para seleccionar ubicación
            archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]
            )

            if archivo:
                # Exportar a Excel
                with pd.ExcelWriter(archivo) as writer:
                    # Hoja de datos principales
                    self.datos.to_excel(writer, sheet_name="Datos_HLI", index=False)

                    # Hoja de resumen de riesgos
                    riesgo_counts = self.datos["Riesgo"].value_counts()
                    riesgo_counts.to_frame("Número de Días").to_excel(
                        writer, sheet_name="Resumen_Riesgos"
                    )

                messagebox.showinfo(
                    "Exportación Exitosa", f"Datos exportados a {archivo}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def importar_datos_excel(self):
        try:
            # Abrir diálogo para seleccionar archivo
            archivo = filedialog.askopenfilename(
                filetypes=[("Archivos Excel", "*.xlsx")]
            )

            if archivo:
                # Importar datos desde Excel
                self.datos = pd.read_excel(archivo, engine="openpyxl")
                # Actualizar gráficos
                self.mostrar_hli_linea()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar: {str(e)}")

    def limpiar_frame(self):
        """Limpia el frame de gráficos"""
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = HLIAnalysisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
