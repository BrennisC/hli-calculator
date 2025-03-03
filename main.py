import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def calcular_hli(bg, rh, ws):
    """
    Calcula el Índice de Carga Calórica (HLI) según las ecuaciones del estudio.
    :param bg: Temperatura del globo negro (°C)
    :param rh: Humedad relativa (%)
    :param ws: Velocidad del viento (m/s)
    :return: Valor del HLI
    """
    if bg > 25:
        hli = 8.62 + (0.38 * rh) + (1.55 * bg) - (0.5 * ws) + np.exp(2.4 - ws)
    else:
        hli = 10.66 + (0.28 * rh) + (1.3 * bg) - ws
    return hli

# Datos simulados
np.random.seed(42)  # Para reproducibilidad
n_dias = 180  # Número de días a simular
temperatura_ambiente = np.random.uniform(25, 35, n_dias)  
humedad_relativa = np.random.uniform(60, 90, n_dias)  
velocidad_viento = np.random.uniform(0.5, 5, n_dias)  
radiacion_solar = np.random.uniform(200, 800, n_dias)  

# Calcular BG (Temperatura del globo negro)
bg = temperatura_ambiente + 0.5 * (radiacion_solar * 0.25) - 0.5 * velocidad_viento

# Crear DataFrame
datos = pd.DataFrame({
    'Dia': range(1, n_dias + 1),
    'Temperatura_Ambiente': temperatura_ambiente,
    'Humedad_Relativa': humedad_relativa,
    'Velocidad_Viento': velocidad_viento,
    'Radiacion_Solar': radiacion_solar,
    'BG': bg
})

# Calcular HLI para cada día
datos['HLI'] = datos.apply(lambda row: calcular_hli(row['BG'], row['Humedad_Relativa'], row['Velocidad_Viento']), axis=1)

# Gráfico de línea para el HLI
plt.figure(figsize=(12, 6))
plt.plot(datos['Dia'], datos['HLI'], label='HLI', color='blue', linewidth=2)
plt.axhline(y=92, color='red', linestyle='--', label='Umbral de estrés leve')
plt.axhline(y=102, color='orange', linestyle='--', label='Umbral de estrés moderado')
plt.title('Variación del Índice de Carga Calórica (HLI)')
plt.xlabel('Día')
plt.ylabel('HLI')
plt.legend()
plt.grid(alpha=0.3)
plt.show()

# Gráfico de dispersión entre temperatura y HLI
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Temperatura_Ambiente', y='HLI', data=datos, color='green', alpha=0.7)
plt.title('Relación entre Temperatura Ambiente y HLI')
plt.xlabel('Temperatura Ambiente (°C)')
plt.ylabel('HLI')
plt.show()

# Gráfico interactivo con Plotly
fig = px.line(datos, x='Dia', y='HLI', title='Variación del Índice de Carga Calórica (HLI)')
fig.add_hline(y=92, line_dash="dash", line_color="red", annotation_text="Umbral de estrés leve")
fig.add_hline(y=102, line_dash="dash", line_color="orange", annotation_text="Umbral de estrés moderado")
fig.update_layout(xaxis_title="Día", yaxis_title="HLI", hovermode="x unified")
fig.show()

def clasificar_riesgo(hli):
    if hli < 92:
        return 'Sin riesgo'
    elif 92 <= hli < 102:
        return 'Riesgo leve'
    elif 102 <= hli < 108:
        return 'Riesgo moderado'
    elif 108 <= hli < 113:
        return 'Riesgo alto'
    else:
        return 'Riesgo extremo'

# Clasificación de riesgo
datos['Riesgo'] = datos['HLI'].apply(clasificar_riesgo)

# Contar la frecuencia de cada categoría de riesgo
riesgo_counts = datos['Riesgo'].value_counts()

# Gráfico de barras
plt.figure(figsize=(10, 6))
sns.barplot(x=riesgo_counts.index, y=riesgo_counts.values, palette='viridis')
plt.title('Distribución de días según nivel de riesgo')
plt.xlabel('Nivel de riesgo')
plt.ylabel('Número de días')
plt.show()

# Guardar los resultados en CSV
datos.to_csv('resultados_hli.csv', index=False)