# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 16:36:06 2024

@author: ncortor
"""

import os
import shutil
import time
import subprocess
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import csv
import psutil
import platform


__author__ = 'Ing. MSc.  PhD(c) Nicolás Cortés-Torres'
__copyright__ = "Copyright 2024, DDL"
__credits__ = ["Nicolás Cortés-Torres"]
__license__ = "GIMHA"
__version__ = "0.1"
__maintainer__ = "Nicolás Cortés-Torres"
__email__ = 'ncortor@doctor.upv.es, ingcortest@gmail.com'
__status__ = "developing"

#%% DEFINICION DE FUNCIONES

################################################################################
# Funcion para reemplazar datos de escala
def replace_scale(vec):
    if "1k" in vec:
        vec = "1000"
    elif "2p5" in vec:
        vec = "2500"
    elif "5k" in vec:
        vec = "5000"
    elif "30m" in vec:
        vec = "30"
    elif "200m" in vec:
        vec = "200"
    elif "500m" in vec:
        vec = "500"
    return vec

################################################################################
# Funcion apra definir la hora actual
def def_hora():
    return time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())

################################################################################
# Funcion para leer la ultima fila del archivo de monitoreo 
def leer_ultima_frecuencia(hwinfo_log_path, freq_col_name):
    """
    Lee la última frecuencia disponible desde el archivo CSV de HWiNFO.
    """
    try:
        with open(hwinfo_log_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            last_row = None
            for row in reader:
                if row[freq_col_name]:
                    last_row = row
        if last_row:
            valor = last_row[freq_col_name].replace(",", ".").strip()
            return float(valor)
    except Exception:
        return None 
    
################################################################################

# Función para ejecutar un .exe y medir el tiempo

def run_exe_monitor(exe_name, path_model, hwinfo_log_path, freq_col_name):
    """
    Ejecuta un ejecutable y mide el tiempo de ejecución, además del promedio de la frecuencia del procesador.

    Parámetros:
    - exe_name: nombre del ejecutable (ej. "Toparc.exe")
    - path_model: ruta al directorio donde se encuentra el ejecutable
    - hwinfo_log_path: ruta completa al archivo .csv generado por HWiNFO
    - freq_col_name: nombre exacto de la columna que contiene la frecuencia en MHz

    Retorna:
    - Diccionario con tiempos y frecuencia promedio
    """
    print("Iniciando monitoreo y ejecución del proceso...")
    freq_values = []

    os.chdir(path_model)
    process = subprocess.Popen([exe_name])

    start_time = time.time()

    while process.poll() is None:
        freq_now = leer_ultima_frecuencia(hwinfo_log_path, freq_col_name)
        if freq_now:
            freq_values.append(freq_now)
            print(f"{time.strftime('%H:%M:%S')} - Frecuencia: {freq_now:.2f} MHz")
        time.sleep(1)

    end_time = time.time()

    exec_time = end_time - start_time #Calcula el tiempo total de ejecución
    freq_promedio = (sum(freq_values) / len(freq_values))/1000 if freq_values else float('nan') #Calcula el promedio de velocidad del procesador

    days = exec_time // 86400
    hours = (exec_time % 86400) // 3600
    minutes = (exec_time % 3600) // 60
    seconds = round(exec_time % 60, 1)
    total_days = exec_time / 86400
    total_hours = exec_time / 3600
    total_minutes = exec_time / 60
    
    return exec_time, days, hours, minutes, seconds, total_days, total_hours, total_minutes, freq_promedio

################################################################################

# Función para extraer la información del equipo

def info_pc(info_equipo, carac):
    # Buscar en todo el DataFrame si contiene el texto "Nombre del procesador:"
    mask = info_equipo.apply(lambda row: row.astype(str).str.contains(carac)).any(axis=1)

    # Obtener los índices (posiciones) donde se encontró
    indices = info_equipo[mask].index.tolist()

    variable = info_equipo.iloc[indices[0], 1]
    
    return variable


#%%###############################################################################################################
##### Codigo para ejecutar Toparc y Hantec - Fase 2 TESIS PHD #######
################################################################################################################
tic = time.time()

print(f"Inicia código - {def_hora()}")


# Paths de trabajo
name_pc = "GIMHABOG" #Nombre del ordenador a analizar
wd_path = "D:/Mod_rendimientos/Modelos/" #Ubicación de los modelos a analizar
wd_tetis = "C:/Tetis9/bin/"  # Directorio de los archivos TETIS .exe
wd_out = "D:/Mod_rendimientos/Res/" #Ubicación de los resultados del codigo
Res_all = f"{wd_out}Results_toparc_hantec_{name_pc}.csv"  # Archivo CSV para guardar los resultados

monitor_file = "D:/Mod_rendimientos/Monitor/monitoreo.csv"
equipo_file = "D:/Mod_rendimientos/Monitor/equipo.csv"
col_monitor = "Relojes núcleo (avg) [MHz]"  # Asegúrate que coincide exactamente con el nombre de la columna


if not os.path.exists(wd_out): #Verifica que existe la carpeta de resultados y la crea 
    os.makedirs(wd_out)
    
   
# Obtener la lista de modelos en la ruta, exceptuando la carpeta de resultados
models = [nombre for nombre in os.listdir(wd_path)
              if os.path.isdir(os.path.join(wd_path, nombre))]

n_models = len(models)

# Inicializar una lista para almacenar los resultados
results = []

print(f"Inicio Analisis de Modelos - {def_hora()}")

#%% Bucle para los modelos
# i = 2
for i in range(len(models)):
    
    wd_model = f"{wd_path}{models[i]}/"  #Defina la ruta del modelo

    print(f"   Procesando modelo: {i+1} de {n_models} - {def_hora()}")
    parts = models[i].split('_')
    cuenca = parts[1].upper()
    escala = replace_scale(parts[2])
    escenario = parts[3].upper()
    modelo = f"{parts[1]}_{parts[2]}_{parts[3]}"

    #%% Modificaciones del FileSSP
    wd_FileSSP = f"{wd_model}FileSSP.tet"
    with open(wd_FileSSP, "r") as file:
        changeFileSSP = file.readlines()  # Leer todas las líneas del archivo en una lista
    
    changeFileSSP[0] = wd_model + "\n"  # Cambiar la línea 1 para ajustar la ruta del modelo
    
    # Escribir las líneas modificadas en FileSSP.txt
    with open(f"{wd_model}FileSSP.txt", "w") as file:
        file.writelines(changeFileSSP)
    
    # Sobrescribir FileSSP.tet con los cambios
    with open(wd_FileSSP, "w") as file:
        file.writelines(changeFileSSP)
    
    #%% Copiar archivos .exe al directorio del modelo
    for exe_file in ["Toparc.exe", "Hantec.exe", "Control.exe", "Tetis.exe"]:
        shutil.copy(os.path.join(wd_tetis, exe_file), wd_model)
        
    #%% Medir tiempos de ejecución para Toparc.exe
    print(f"       Generando Topolco: {models[i]} - {def_hora()}")
    
    Res_toparc = run_exe_monitor("Toparc.exe", wd_model, monitor_file, col_monitor) #ejecuta toparc y calcula tiempos y velocidad
    
    # Lectura de Topolco
    wd_topolco = f"{wd_model}Topolco.sds" #directorio de topolco
    with open(wd_topolco, "r") as file:
        topolco = file.readlines()  # Leer todas las líneas del archivo en una lista
    
    # Dividir cada línea en columnas basadas en espacios
    topolco = [line.split() for line in topolco]
    celdas = int(topolco[6][1]) # numero de celdas de la cuenca
            
    if os.path.isfile(wd_topolco):
        # Obtener el tamaño del archivo en bytes
        topolco_tamaño_bytes  = os.path.getsize(wd_topolco)
        topolco_tamaño_kb = topolco_tamaño_bytes / 1024
        topolco_tamaño_mb = topolco_tamaño_kb / 1024
        topolco_tamaño_gb = topolco_tamaño_mb / 1024
    
    #%% Medir tiempos de ejecución para Hantec.exe
    print(f"       Generando Hantec: {models[i]} - {def_hora()}")
    
    Res_hantec = run_exe_monitor("Hantec.exe", wd_model, monitor_file, col_monitor) #ejecuta hantec y calcula tiempos y velocidad
  
    # Lectura de Hantec
    wd_hantec = f"{wd_model}Hantec.sds" # directorio de hantec

    if os.path.isfile(wd_hantec):
        # Obtener el tamaño del archivo en bytes
        hantec_tamaño_bytes  = os.path.getsize(wd_hantec)
        hantec_tamaño_kb = hantec_tamaño_bytes / 1024
        hantec_tamaño_mb = hantec_tamaño_kb / 1024
        hantec_tamaño_gb = hantec_tamaño_mb / 1024
    
    #%% Medir tiempos de ejecución para Hantec.exe
    # Agregar los resultados a la lista
    results.append([
        name_pc, cuenca, escala, escenario, modelo, celdas,
        *Res_toparc, *Res_hantec,
        topolco_tamaño_mb, topolco_tamaño_gb,
        hantec_tamaño_mb, hantec_tamaño_gb,
    ])
    print(f"   Procesando modelo: {i+1} de {n_models} - {def_hora()}")
    
    
#%% Crear un DataFrame de pandas con los resultados  
print(f"Creando Dataframe - {def_hora()}")

df = pd.DataFrame(results, columns=[
    'Equipo', 'Cuenca', 'Escala','Escenario', 'Modelo', 'Celdas',
    'Toparc Time', 'Toparc Days', 'Toparc Hours', 'Toparc Minutes', 'Toparc Seconds',
    'Toparc Total Days', 'Toparc Total Hours', 'Toparc Total Minutes', 'Vel_Toparc',
    'Hantec Time', 'Hantec Days', 'Hantec Hours', 'Hantec Minutes', 'Hantec Seconds',
    'Hantec Total Days', 'Hantec Total Hours', 'Hantec Total Minutes','Vel_Hantec',
    'Tamaño Topolco mb', 'Tamaño Topolco gb',
    'Tamaño Hantec mb', 'Tamaño Hantec gb'
])


#%% Extraer info del equipo
print(f"Agregando columnas extra - {def_hora()}")

# Leer el archivo como texto plano usando codificación robusta "utf-8"
with open(equipo_file, encoding="utf-8") as f:
    info_equipo = f.readlines()
    
info_equipo = pd.DataFrame(info_equipo)
info_equipo = info_equipo[0].str.strip().str.split(",", expand=True)

procesador = info_pc(info_equipo, "Nombre del procesador:") 
memoria_ram_gb = info_pc(info_equipo, "Tamaño de memoria total:") 
nucleos = info_pc(info_equipo, "Número de núcleos de procesador:") 
procesadores_logicos = info_pc(info_equipo, "Número de procesadores lógicos:") 

# Crear columnas repetidas con la misma info para todas las filas del DataFrame
df['Procesador'] = procesador
df['Memoria Ram Gb'] = memoria_ram_gb
df['Nucleos'] = nucleos
df['Procesadores logicos'] = procesadores_logicos

#%% Guardar el DataFrame en un archivo CSV
print(f"Guardando resultados - {def_hora()}")

df.to_csv(Res_all, index=False)

print(f"Fin ejecución - {def_hora()}")


##########################################################################################################################
#################                             FINAL CODIGO                       #########################################
##########################################################################################################################

run_time = (time.time() - tic)
hours_ = run_time // 3600.0
minutes_ = round((run_time / 3600.0 - hours_) * 60.0, 1)
text_ = f'Execution total time was {hours_} hours and {minutes_} minutes'
len_text = len(text_)
len_print = len_text + 2 * 10
len_blank = (len_print - 2)
print(len_print * '#')
print('#' + len_blank * ' ' + '#')
print('#' + 9 * ' ' + text_ + 9 * ' ' + '#')
print('#' + len_blank * ' ' + '#')
print(len_print * '#')


