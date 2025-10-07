# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 13:31:52 2025

@author: ncortor
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 15:52:39 2024

@author: ncortor
"""

import os
import shutil
import time

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
# Funcion apra definir la hora actual
def def_hora():
    return time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())


def copiar_archivos(src_dir, dst_dir, archivos):
    """
    Copia archivos específicos desde una ubicación a otra, reemplazando los archivos existentes.

    :param src_dir: Directorio de origen donde se encuentran los archivos.
    :param dst_dir: Directorio de destino donde se copiarán los archivos.
    :param archivos: Lista de nombres de archivos a copiar.
    """
    # Crear el directorio de destino si no existe
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    for archivo in archivos:
        src_path = os.path.join(src_dir, archivo)
        
        # Verificar si el archivo es 'Hantec_5k_1990.sds' y cambiar el nombre en el destino
        if "Hantec" in archivo:
            dst_path = os.path.join(dst_dir, 'Hantec.sds')
        elif "Paramgeo" in archivo:
            dst_path = os.path.join(dst_dir, 'Paramgeo.txt')
        else :
            dst_path = os.path.join(dst_dir, archivo)
           
        if os.path.exists(src_path):
            # Copiar el archivo al directorio de destino
            shutil.copy2(src_path, dst_path)
            # print(f'Archivo {archivo} copiado a {dst_path}')
        else:
            print(f'Archivo {archivo} no encontrado en {src_path}')

# Especifica la ruta de origen y destino



#%%###############################################################################################################
##### Codigo para ejecutar Toparc y Hantec - Fase 4 TESIS PHD #######
################################################################################################################
tic = time.time()

print(f"Inicia código - {def_hora()}")

origen = "D:/Mod_rendimientos/Res/" # Ruta de los archivos a copiar
path = "D:/Mod_rendimientos/Modelos/" # Ruta raíz de las carpetas donde se va a copiar

# Obtener la lista de modelos en la ruta, exceptuando la carpeta de resultados
models = [nombre for nombre in os.listdir(path)
              if os.path.isdir(os.path.join(path, nombre))]

n_models = len(models)

#%% Bucle para los modelos
# i = 4
for i in range(len(models)):
    
    print(f"   Copiando a {models[i]}: {i+1} de {n_models} - {def_hora()}")
    
    wd_model = f"{path}{models[i]}/"  #Defina la ruta del modelo
    
    # Especifica los archivos a copiar
    archivos = ['Calib.txt', 'FactorETmes.txt']  # Archivo a copiar
    
    # Llama a la función para copiar los archivos
    copiar_archivos(origen, wd_model, archivos)
        
        
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