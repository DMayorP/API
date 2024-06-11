# 1. importando los paquetes
from st_aggrid import AgGrid 
import streamlit as st
import pandas as pd 
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report
#from pandas_profiling import ProfileReport
#from pydantic import BaseSettings
from ydata_profiling import ProfileReport
from  PIL import Image
import os
import re
import numpy as np
from datetime import datetime
from pydantic import BaseSettings
from datetime import datetime, timedelta
from streamlit_date_picker import date_range_picker, date_picker, PickerType

# paquetes pdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from streamlit_extras.stateful_button import button

import zipfile
import os
import time
# FUNCIONES DE PDF 

######################
#      funciones PDF
######################


#######################################
# FUENTES
######################################
# Fuentes de la cabecera
fuente_nombre_formato = 'Helvetica-Bold'
tamano_fuente_formato = 10
fuente_codigo_formato = 'Helvetica'
tamano_codigo_formato = 8

# Fuentes de las tablas (de indicadores)
fuente_cabecera_tabla = 'Helvetica-Bold'
tamano_cabecera_tabla = 11
fuente_contenido_tabla = "Helvetica"
tamano_contenido_tabla = 10
tamano_contenido_estrellas = 12

# Fuentes del contenido del documento
fuente_titulos = 'Helvetica-Bold'
tamano_titulos = 11
fuente_contenido = "Helvetica"
tamano_contenido = 10

# Fuentes del pie de pagina
fuente_num_pagina = 'Helvetica'
tamano_num_pagina = 8

# % de interlineado
interlineado = 0.4      # 40%
m_off = 0.05            # Parametro para estimar el espacio entre una palabra y su definición

#######################################
# DATOS DE LA CABECERA Y PIE DE PAGINA
#######################################
# Crear la tabla de la cabecera
datos_cabecera = [
    ['', 'FORMATO DE INSPECCIÓN Y ANÁLISIS  DE DATOS', 'CÓDIGO: F-IC-G07-01'],
    ['', '', 'Versión: 03'],
    ['', '', 'Vigencia: 13-09-2022']
]

# Logo y título de la cabecera
ruta_logo = "logo-minjusticia2.png"  # Cambio en la ruta del logo

# Pie de página
titulo_footer = "Ministerio de Justicia y del Derecho"

#######################################
# MERGENES DEL CONTENIDO DEL DOCUMENTO
######################################
margen_izquierdo = 60
margen_derecho = 60
margen_superior = 150
margen_inferior = 50
ancho, alto = letter
ancho_util = ancho - margen_izquierdo - margen_derecho
alto_util = alto - margen_superior - margen_inferior

# Margenes para ubicar el logo
margen_izquierdo_logo = 75
margen_superior_logo = 25
ancho_logo = 80
alto_logo = 32

#######################################
# PARTES ESTATICAS DEL DOCUMENTO
######################################
# Defina aca los indicadores cualitativos con la estructura que se indica
param_cuanti = {
    "Exactitud semántica:": "hace referencia a la propiedad de los datos de pertenecer al tipo de dato correcto.",
    "Completitud:": "hace referencia a que todos los datos que se requieren estén completos",
    "Dimensiones mínimas:": "son las dimensiones mínimas dadas para completar una solicitud o tarea.",
    "Unicidad:": "Esta propiedad asegura que los datos que deben ser únicos lo sean realmente.",
    "Exactitud sintáctica":"asegura que los datos reflejen correctamente lo que representan",
    "Consistencia":"grado en el que los datos están libres de contradicción y son coherentes con otros datos en un contexto de uso específico."
} #AGREGAR OTRAS DEFINICIONES

# Defina aca los indicadores cuantitatitvos con la estructura que se indica
param_cuali = {
    "Confiabilidad:": "grado en el que los datos tienen atributos que se adhieren a estándares, convenciones o normativas vigentes y reglas similares referentes a la calidad de datos en un contexto de uso específico.",
    "Actualidad:": "Grado en el que los datos tienen atributos que tienen la edad correcta en un contexto de uso específico."
}

biblio_fuentes= {
    "1": "DAMA International. (2017). DAMA-DMBOK: Cuerpo de Conocimiento de Gestión de Datos (2ª ed.). Technics Publications",
    "2": "DAMA International. (2017). DAMA-DMBOK: Cuerpo de Conocimiento de Gestión de Datos (2ª ed.). Technics Publications"
}



#############################################################
# Obtener las estrellas
#############################################################
def obtener_estrellas(calificacion):
    entero = int(calificacion)
    fraccion = calificacion - entero
    estrellas = ''

    # Fraccion
    if fraccion < 0.1:
        estrella_fraccion = '✩'
    elif  fraccion >= 0.1 and fraccion <= 0.33:
        estrella_fraccion = '✬'
    elif  fraccion > 0.33 and fraccion <= 0.66:
        estrella_fraccion = '✮'
    elif  fraccion > 0.66 and fraccion <= 0.9:
        estrella_fraccion = '✭'
    else:         
        estrella_fraccion = '★'

    # Estrellas completas
    i = 0
    while i < entero:
        estrellas += '★'
        i += 1

    if entero < 5:
        # Estrella fraccion
        estrellas = estrellas + estrella_fraccion

        # Estrellas blancas
        i += 1
        while i < 5:
            estrellas += '✩'
            i += 1
        
    return estrellas


#############################################################
# Agregar al informe la tabla de indicadores
#############################################################
def agregar_tabla_indicadores(puntero_y, lista_indicadores, doc_pdf, cabecera, numero_pagina):

    # Debug
    # print(f"agregar_tabla_indicadores puntero_y inicial: {puntero_y}, numero_pagina: {numero_pagina}")

    # Definir el tamaño de la página
    ancho, alto = letter
    
    estilo_titulo = ParagraphStyle(name='Cell', wordWrap='Whitespace', alignment=1, fontSize=tamano_cabecera_tabla, fontName=fuente_cabecera_tabla)
    estilo_cen = ParagraphStyle(name='Cell', wordWrap='None', alignment=1, fontSize=tamano_contenido_tabla, fontName=fuente_contenido_tabla)
    estilo_est = ParagraphStyle(name='Cell', wordWrap='None', alignment=1, fontSize=tamano_contenido_estrellas, fontName=fuente_contenido_tabla) 
    estilo_izq = ParagraphStyle(name='Cell', wordWrap='None', alignment=0, fontSize=tamano_contenido_tabla, fontName=fuente_contenido_tabla)

    tabla_data = []
    for pos_fila, fila in enumerate(lista_indicadores):
        row_data = []
        for pos_col, cell_text in enumerate(fila):

            if pos_fila == 0:
                estilo_celda = estilo_titulo    # Centrar horizontalmente la primera fila
            else:
                if pos_col == 1:
                    estilo_celda = estilo_cen
                elif pos_col == 2:
                    estilo_celda = estilo_est
                else:
                    estilo_celda = estilo_izq

            row_data.append(Paragraph(cell_text, estilo_celda))

        tabla_data.append(row_data)

    tabla = Table(tabla_data, colWidths=[120, 80, 80, 220])

    # Estilo del marco de la tabla
    estilo_tabla = TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),      # Fondo gris claro solo en la primera fila
        ("VALIGN", (0, 0), (-1, -1), "TOP")])                    # Alinear verticalmente arriba
    
    # Aplicar el estilo a la tabla
    tabla.setStyle(estilo_tabla)

    # Obtener el ancho de la tabla
    tabla.wrapOn(doc_pdf, ancho, alto)
    ancho_tabla, alto_tabla = tabla.wrap(0, 0)
    
    # print(f"alto_tabla: {alto_tabla}")

    
    # Verificar si nos hemos quedado sin espacio en la página            
    if puntero_y - alto_tabla <= margen_inferior :

        # Agregar título y número de página en el pie de página
        doc_pdf.setFont(fuente_num_pagina, tamano_num_pagina)
        doc_pdf.drawString(ancho // 2 - len(titulo_footer) * 2, margen_inferior - 20, titulo_footer)
        doc_pdf.drawString(ancho - margen_derecho - 50, margen_inferior - 20, f"Página {numero_pagina}")


        doc_pdf.showPage()  # Cambiar a una nueva página
        imprimir_cabecera(cabecera, doc_pdf)
        puntero_y = alto_util + margen_inferior
        numero_pagina += 1

    pos_x = ancho // 2 - ancho_tabla / 2
    pos_y = puntero_y + 50 - alto_tabla

    tabla.drawOn(doc_pdf, pos_x, pos_y)
    puntero_y -= alto_tabla

    # Debug
    # print(f"agregar_tabla_indicadores puntero_y final: {puntero_y}, numero_pagina: {numero_pagina}")

    return puntero_y, numero_pagina

#############################################################
# Agregar al informe la tabla de indicadores
#############################################################
def agregar_tabla_cualitativa(puntero_y, lista_indicadores, doc_pdf, cabecera, numero_pagina):

    # Debug
    # print(f"agregar_tabla_cualitativa puntero_y inicial: {puntero_y}, numero_pagina: {numero_pagina}")

    # Definir el tamaño de la página
    ancho, alto = letter
    
    estilo_titulo = ParagraphStyle(name='Cell', wordWrap='Whitespace', alignment=1, fontSize=tamano_cabecera_tabla, fontName=fuente_cabecera_tabla)
    estilo_izq = ParagraphStyle(name='Cell', wordWrap='None', alignment=0, fontSize=tamano_contenido_tabla, fontName=fuente_contenido_tabla)

    tabla_data = []
    for pos_fila, fila in enumerate(lista_indicadores):
        row_data = []
        for pos_col, cell_text in enumerate(fila):

            if pos_fila == 0:
                estilo_celda = estilo_titulo    # Centrar horizontalmente la primera fila
            else:
                estilo_celda = estilo_izq
    
            row_data.append(Paragraph(cell_text, estilo_celda))

        tabla_data.append(row_data)

    tabla = Table(tabla_data, colWidths=[120, 220])

    # Estilo del marco de la tabla
    estilo_tabla = TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),      # Fondo gris claro solo en la primera fila
        ("VALIGN", (0, 0), (-1, -1), "TOP")])                    # Alinear verticalmente arriba
    
    # Aplicar el estilo a la tabla
    tabla.setStyle(estilo_tabla)

    # Obtener el ancho de la tabla
    tabla.wrapOn(doc_pdf, ancho, alto)
    ancho_tabla, alto_tabla = tabla.wrap(0, 0)
    

    if puntero_y - alto_tabla <= margen_inferior:
        # Agregar título y número de página en el pie de página
        doc_pdf.setFont(fuente_num_pagina, tamano_num_pagina)
        doc_pdf.drawString(ancho // 2 - len(titulo_footer) * 2, margen_inferior - 20, titulo_footer)
        doc_pdf.drawString(ancho - margen_derecho - 50, margen_inferior - 20, f"Página {numero_pagina}")

        doc_pdf.showPage()  # Cambiar a una nueva página
        imprimir_cabecera(cabecera, doc_pdf)
        puntero_y = alto_util + margen_inferior
        numero_pagina += 1

    pos_x = ancho // 2 - ancho_tabla / 2
    pos_y = puntero_y + 50 - alto_tabla

    tabla.drawOn(doc_pdf, pos_x, pos_y)
    puntero_y -= alto_tabla

    # Debug
    # print(f"agregar_tabla_cualitativa puntero_y final: {puntero_y}, numero_pagina: {numero_pagina}")

    return puntero_y, numero_pagina


#############################################################
# Convertir diccionadio de indicadires a listado para la tabla
#############################################################
def dicc_listado_cuanti(cal_calidad):

    data_indicador = []     # inicializar listado
    sum_total = 0           # suma de total de calificaciones
    cant_ind = 0            # cantidad de indicadores

    # Itere por cada indicador
    for indicador in cal_calidad.values():

        sum_total += indicador[1]
        cant_ind += 1
        estrellas = obtener_estrellas(indicador[1])
        indicador[1] = str(round(indicador[1], 1))

        indicador.insert(2, estrellas)
        data_indicador.append(indicador)

    prom_total = str(round(sum_total / cant_ind, 1))
    estrellas = obtener_estrellas(sum_total / cant_ind)

    fila_cabecera = ['Dimensiones de calidad', 'Calificación', 'Gráfica calificación', 'Observaciones']
    fila_total = ['Total', prom_total, estrellas, '']

    data_indicador.insert(0, fila_cabecera)
    data_indicador.append(fila_total)

    return data_indicador

#############################################################
# Convertir diccionadio de indicadires a listado para la tabla
#############################################################
def dicc_listado_cuali(cal_calidad):

    data_indicador = []     # inicializar listado

    # Itere por cada indicador
    for indicador in cal_calidad.values():
        data_indicador.append(indicador)

    fila_cabecera = ['Dimensiones de calidad', 'Observaciones']
    data_indicador.insert(0, fila_cabecera)

    return data_indicador



#######################################
# CONFIGURAR_CABECERA
#######################################
def configurar_cabecera():

    # Defina la tabla que actuará como cabecera
    cabecera = Table(datos_cabecera, colWidths=[120, 260, 120], rowHeights=[15, 15, 15])
    
    # Fusionar las celdas de la primera columna
    cabecera.setStyle(TableStyle([('SPAN', (0, 0), (0, 2))]))

    # Fusionar las celdas de la segunda columna y centrar el texto horizontal y verticalmente
    cabecera.setStyle(TableStyle([
        ('SPAN', (1, 0), (1, 2)),
        ('ALIGN', (1, 0), (1, 2), 'CENTER'), ('VALIGN', (1, 0), (1, 2), 'MIDDLE'),
        ('FONT', (1, 0), (1, 2), fuente_nombre_formato, tamano_fuente_formato)]))

    # Ajustar el tamaño de fuente y alineacion para las 3 celdas de la derecha
    cabecera.setStyle(TableStyle([
        ('FONT', (2, 0), (2, -1), fuente_codigo_formato, tamano_codigo_formato),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (2, 0), (2, -1), 'MIDDLE')]))

    # Estilo del marco de la tabla
    estilo_tabla = TableStyle([('GRID', (0, 0), (-1, -1), 1, (0, 0, 0))])
    cabecera.setStyle(estilo_tabla)

    return cabecera


#######################################
# GENERAR INFORME DE CALIDAD EN PDF
#######################################
def imprimir_cabecera(tabla, doc_pdf):

    # Debug
    # print("\n******\nNueva cabecera\n*******\n")

    # Dibujar la cabecera del archivo (Ficha del formato de calidad)
    tabla.wrapOn(doc_pdf, ancho, alto)
    ancho_tabla, _ = tabla.wrap(0, 0)
    tabla.drawOn(doc_pdf, ancho // 2 - ancho_tabla / 2, alto - 80)

    # Agregar el logo y título en el header
    doc_pdf.drawImage(ruta_logo, margen_izquierdo_logo, alto - margen_superior_logo - 50, width=ancho_logo, height=alto_logo)

    return

#######################################
# ITERAR SOBRE UN PARRAFO
#######################################
# RAULP OJOO: desagregar para dejar aparte la función de agregar nueva pagina, para su uso por la tabla

def iterar_diccionario(puntero_y, diccionario, doc_pdf, cabecera, numero_pagina):
    
    # Debug
    # print(f"iterar_diccionario puntero_y inicial: {puntero_y}, numero_pagina: {numero_pagina}")

    # Iterar sobre las líneas del texto
    for palabra_clave, palabra_valor in diccionario.items():
        puntero_y -= tamano_titulos * (1+interlineado)  # Mueva el puntero a la siguiente linea

        # Dividir la línea en palabras
        palabras = palabra_clave.split()

        # Inicializar la línea actual

        linea_actual = ''

        # Iterar sobre las palabras y escribir en el PDF
        for palabra in palabras:
            
            # Inicie con una cabecera
            # imprimir_cabecera(cabecera, doc_pdf) #??? la sobreimpresión de la cabecera no se nota

            # print(f"Lin actual 1: {linea_actual}")

            # Verificar si la palabra cabe en la línea actual
            if doc_pdf.stringWidth(linea_actual + palabra + ' ', fuente_titulos) <= ancho_util:
                # Agregar la palabra a la línea actual
                linea_actual += palabra + ' '
            else:
                # Si no cabe, dibujar la línea actual en el PDF y avanzar a la siguiente línea
                doc_pdf.setFont(fuente_titulos, tamano_titulos)
                doc_pdf.drawString(margen_izquierdo, margen_inferior + puntero_y, linea_actual[:-1])  # Excluir el último espacio
                puntero_y -= tamano_titulos * (1+interlineado)  # Espaciado de línea
                linea_actual = palabra + ' '

                # print(f"Lin actual 2: {linea_actual}")

            # Verificar si nos hemos quedado sin espacio en la página            
            if puntero_y <= margen_inferior:
                # Agregar título y número de página en el pie de página
                doc_pdf.setFont(fuente_num_pagina, tamano_num_pagina)
                doc_pdf.drawString(ancho // 2 - len(titulo_footer) * 2, margen_inferior - 20, titulo_footer)
                doc_pdf.drawString(ancho - margen_derecho - 50, margen_inferior - 20, f"Página {numero_pagina}")


                doc_pdf.showPage()  # Cambiar a una nueva página
                imprimir_cabecera(cabecera, doc_pdf)

                puntero_y = alto_util + margen_inferior - tamano_titulos
                numero_pagina += 1
                
        # Dibujar la última línea si es necesario
        if linea_actual:
            doc_pdf.setFont(fuente_titulos, tamano_titulos)
            doc_pdf.drawString(margen_izquierdo, margen_inferior + puntero_y, linea_actual[:-1])  # Excluir el último espacio

###### Palabra valor

        # Dividir la línea en palabras
        palabras2 = palabra_valor.split()
        longitud_clave = doc_pdf.stringWidth(linea_actual + ": ", fuente_contenido)
        espacios = m_off * longitud_clave

        # Inicializar la línea actual
        linea_actual2 = ''

        # Iterar sobre las palabras y escribir en el PDF
        for palabra in palabras2:
            
            # Inicie con una cabecera
            # imprimir_cabecera(cabecera, doc_pdf) #????
            
            # Verificar si la palabra cabe en la línea actual
            if doc_pdf.stringWidth(linea_actual + linea_actual2 + palabra + ' ', fuente_contenido) <= ancho_util:
                # Agregar la palabra a la línea actual
                linea_actual2 += palabra + ' '
            else:
                # Si no cabe, dibujar la línea actual en el PDF y avanzar a la siguiente línea

                doc_pdf.setFont(fuente_contenido, tamano_contenido)
                # print(f"Draw1: {linea_actual2[:-1]}")
                if not linea_actual:
                    offset = 0
                else:
                    offset = espacios
                doc_pdf.drawString(margen_izquierdo + longitud_clave + offset, margen_inferior + puntero_y, linea_actual2[:-1])  # Excluir el último espacio
                puntero_y -= tamano_contenido * (1+interlineado)  # Espaciado de línea
                linea_actual = ''
                longitud_clave = 0
                linea_actual2 = palabra + ' '

                # print(f"Lin actual 2: {linea_actual2}")


            # Verificar si nos hemos quedado sin espacio en la página            
            if puntero_y <= margen_inferior:
                # Agregar título y número de página en el pie de página
                doc_pdf.setFont(fuente_num_pagina, tamano_num_pagina)
                doc_pdf.drawString(ancho // 2 - len(titulo_footer) * 2, margen_inferior - 20, titulo_footer)
                doc_pdf.drawString(ancho - margen_derecho - 50, margen_inferior - 20, f"Página {numero_pagina}")

                doc_pdf.showPage()  # Cambiar a una nueva página
                imprimir_cabecera(cabecera, doc_pdf)
                puntero_y = alto_util + margen_inferior - tamano_contenido
                numero_pagina += 1
                
        # Dibujar la última línea si es necesario
        if linea_actual2:
            try:
                if not linea_actual:
                    offset = 0
                else:
                    try:
                        offset = espacios
                    except:
                        print('eror')
                        st.warning('seleccione al menos una columna para el análisis', icon="⚠️")
                        return None
                                
                doc_pdf.setFont(fuente_contenido, tamano_contenido)
                # print(f"Draw2: {linea_actual2[:-1]}")
                doc_pdf.drawString(margen_izquierdo + longitud_clave + offset, margen_inferior + puntero_y, linea_actual2[:-1])  # Excluir el último espacio
            except:
                st.warning('seleccione al menos una columna para el análisis', icon="⚠️")
                

    puntero_y -= tamano_contenido * (1+interlineado)  # Mueva el puntero a la siguiente linea

    # Debug
    # print(f"iterar_diccionario puntero_y final: {puntero_y}, numero_pagina: {numero_pagina}")

    return puntero_y, numero_pagina

#######################################
# IMPRIMIR TEXTO
#######################################
def imprimir_parrafo(puntero_y, parrafo, doc_pdf, cabecera, numero_pagina, negrilla, salto_pre, salto_pos):

    # Debug
    # print(f"imprimir_parrafo puntero_y inicial: {puntero_y}, numero_pagina: {numero_pagina}")

    # Si se quiere negrilla
    if negrilla:
        fuente_parrafo = fuente_titulos
        tamano_parrafo = tamano_titulos
    else:
        fuente_parrafo = fuente_contenido
        tamano_parrafo = tamano_contenido

    for _ in range(salto_pre):
        puntero_y -= tamano_parrafo * (1 + interlineado)  # Mueva el puntero a la siguiente linea

    # Dividir la línea en palabras
    palabras = parrafo.split()

    # Inicializar la línea actual
    linea_actual = ''

    # Iterar sobre las palabras y escribir en el PDF
    for palabra in palabras:
        
        # Inicie con una cabecera
        # imprimir_cabecera(cabecera, doc_pdf)

        # Verificar si la palabra cabe en la línea actual
        if doc_pdf.stringWidth(linea_actual + palabra + ' ', fuente_parrafo) <= ancho_util:
            # Agregar la palabra a la línea actual
            linea_actual += palabra + ' '
        else:
            # Dibujar la línea actual en el PDF y avanzar a la siguiente línea
            doc_pdf.setFont(fuente_parrafo, tamano_parrafo)
            doc_pdf.drawString(margen_izquierdo, margen_inferior + puntero_y, linea_actual[:-1])  # Excluir el último espacio
            puntero_y -= tamano_parrafo * (1+interlineado)  # Espaciado de línea
            linea_actual = palabra + ' '

        # Verificar si nos hemos quedado sin espacio en la página            
        if puntero_y <= margen_inferior:
            # Agregar título y número de página en el pie de página
            doc_pdf.setFont(fuente_num_pagina, tamano_num_pagina)
            doc_pdf.drawString(ancho // 2 - len(titulo_footer) * 2, margen_inferior - 20, titulo_footer)
            doc_pdf.drawString(ancho - margen_derecho - 50, margen_inferior - 20, f"Página {numero_pagina}")


            doc_pdf.showPage()  # Cambiar a una nueva página
            imprimir_cabecera(cabecera, doc_pdf)
            puntero_y = alto_util + margen_inferior - tamano_parrafo
            numero_pagina += 1
    # Dibujar la última línea si es necesario
    if linea_actual:
        try:
            doc_pdf.setFont(fuente_parrafo, tamano_parrafo)
            doc_pdf.drawString(margen_izquierdo, margen_inferior + puntero_y, linea_actual[:-1])  # Excluir el último espacio
        except:
            #print('error miguel')
            st.warning('seleccione al menos una columna para el análisis', icon="⚠️")
            return None
    for _ in range(salto_pos):
        puntero_y -= tamano_parrafo * (1 + interlineado)  # Mueva el puntero a la siguiente linea

    # Debug
    # print(f"imprimir_parrafo puntero_y final: {puntero_y}, numero_pagina: {numero_pagina}")

    return puntero_y, numero_pagina


#######################################
# GENERAR INFORME DE CALIDAD EN PDF
#######################################
def generar_pdf(nombre_archivo, dicc_unico, tabla_indicadores, tabla_cualitativa):
    
    # # Dividir el texto en parrafos separados por retorno de carro "\n"
    # parrafos = texto.split('\n')

    # Crear el informe PDF
    informe = canvas.Canvas(nombre_archivo, pagesize=letter)
    
    # Configurar cabecera del informe
    cabecera = configurar_cabecera()

    #NEW
    imprimir_cabecera(cabecera, informe)

    # Inicializar variables para el bucle
    # puntero_y va de 0 en el borde inferior de la hora a su valor maximo en el borde superior
    # un puntero en x no se define, ya que es gobernado por la impresión de caracteres (drawString) en cada línea
    puntero_y = alto_util + margen_inferior     
    linea_actual = ''
    numero_pagina = 1

    parrafo = "OBJETIVO"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, True, 1, 1)
        
    parrafo = "Realizar la revisión y aseguramiento de calidad de la información recibida y procesada por las diferentes fuentes externas o internas del Ministerio de Justicia y del Derecho"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, False, 1, 1)

    parrafo = "INFORMACION GENERAL"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, True, 1, 1)
    puntero_y, numero_pagina = iterar_diccionario(puntero_y, dicc_unico, informe, cabecera, numero_pagina)

    parrafo = "PARÁMETROS DE CALIDAD DE DATOS"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, True, 1, 1)

    parrafo = "En esta sección se describen los diferentes parámetros que evalúan la calidad del ––conjunto de datos, estos se definen a continuación:"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, False, 1, 1)

    parrafo = "Dimensiones cuantitativas"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, True, 1, 1)
    puntero_y, numero_pagina = iterar_diccionario(puntero_y, param_cuanti, informe, cabecera, numero_pagina)

    t_indicadores = dicc_listado_cuanti(tabla_indicadores)
    puntero_y, numero_pagina = agregar_tabla_indicadores(puntero_y, t_indicadores, informe, cabecera, numero_pagina)

    parrafo = "Dimensiones cualitativas"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, True, 2, 1)
    puntero_y, numero_pagina = iterar_diccionario(puntero_y, param_cuali, informe, cabecera, numero_pagina)

    t_cualitativa = dicc_listado_cuali(tabla_cualitativa)
    puntero_y, numero_pagina = agregar_tabla_cualitativa(puntero_y, t_cualitativa, informe, cabecera, numero_pagina)

    #### agregado por miguel 
    parrafo = "Bibliografía"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, True, 2, 1)
    # puntero_y, numero_pagina = iterar_diccionario(puntero_y, biblio_fuentes, informe, cabecera, numero_pagina)
    parrafo = "Ministerio de Justicia y del Derecho. (2020, 11 de diciembre). Guía Atributos de Calidad. Recuperado el 2 de febrero de 2024, de https://sii.minjusticia.gov.co/app.php/staff/document/tree/viewPublic?id=1640"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, False, 1, 1)
    # puntero_y, numero_pagina = iterar_diccionario(puntero_y, biblio_fuentes, informe, cabecera, numero_pagina)
    parrafo = "Pipino, L. L., Lee, Y. W., & Wang, R. Y. (2017). Data Management Body of Knowledge (2nd ed.). Hoboken, NJ: John Wiley & Sons"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, False, 1, 1)
    #Google Cloud. (2024, May 26). Preparación de datos para la predicción con datos tabulares. Google Cloud. https://cloud.google.com/vertex-ai/docs/tabular-data/forecasting/prepare-data?hl=es-419#csv
    parrafo = "Google Cloud. (2024, May 26). Preparación de datos para la predicción con datos tabulares. Google Cloud. https://cloud.google.com/vertex-ai/docs/tabular-data/forecasting/prepare-data?hl=es-419#csv"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, False, 1, 1)
    #ISO 25000. (n.d.). ISO/IEC 25012: Data Quality Models. Retrieved May 26, 2024, from https://iso25000.com/index.php/normas-iso-25000/iso-25012?start=5
    # parrafo = "ISO 25000. (n.d.). ISO/IEC 25012: Data Quality Models. Retrieved May 26, 2024, from https://iso25000.com/index.php/normas-iso-25000/iso-25012?start=5"
    # puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, False, 1, 1)
    #https://gobiernodigital.mintic.gov.co/692/articles-179118_recurso_5.pdf
    parrafo = "Ministerio de Tecnologías de la Información y las Comunicaciones. (s.f.). Guia de Calidad de Datos. MinTIC. https://gobiernodigital.mintic.gov.co/692/articles-179118_recurso_5.pdf"
    puntero_y, numero_pagina = imprimir_parrafo(puntero_y, parrafo, informe, cabecera, numero_pagina, False, 1, 1)
    
    
    ### hasta aqui agregado por miguel/

    # Agregar número de página en el último pie de página
    informe.setFont(fuente_num_pagina, tamano_num_pagina)
    informe.drawString(ancho // 2 - len(titulo_footer) * 2, margen_inferior - 20, titulo_footer)
    informe.drawString(ancho - margen_derecho - 50, margen_inferior - 20, f"Página {numero_pagina}")

    # Guardar el PDF
    informe.save()

    return



#### FUNCIONES DE GUARDADO DE DATOS 

def guardar_datos(EncargadoMJD, AreaEncargadoMJD, FechaRecepExtrac, date_range_str_out, PeriodoActInfo,NombreArchivo,TipoFuenteInfo, EntidadesFuenteInfo,
                   contactoEncargadoInfo,DirecEncargadoInfo ,FuenteEntradaInfo, DireccPagWeb, MedConsEntreInfo, FonrmatInfo,ObsConsis, ObsExactSemant,ObsUnicidad,ObsComplet,
                   ObsExactSintact, ObsDimMin,obsActualidad, ObsConfiabilid,NumRegInconsistentes,NumRegsinExacSem):
    # Aquí puedes guardar los datos en las variables que desees
    # Por ejemplo, podrías guardarlos en un diccionario o en una base de datos
    st.write("Encargado de diligenciar el formato (MJD):", EncargadoMJD)
    st.write("Área del encargado de diligenciar el formato (MJD):", AreaEncargadoMJD)
    st.write("Fecha de recepción o de extracción:", FechaRecepExtrac)
    st.write("Periodo del reporte inicio:",date_range_str_out )
    st.write("Periodicidad de actualización de la información:", PeriodoActInfo)
    st.write("Nombre del archivo: ", NombreArchivo)
    st.write("Tipo de la fuente de información:",TipoFuenteInfo )
    st.write("Entidad(es) de la fuente de la información:", EntidadesFuenteInfo)
    st.write("Contacto encargado de enviar la información:",contactoEncargadoInfo )
    st.write("Dependencia encargada de enviar la información: ",DirecEncargadoInfo)
    st.write("Dependencia encargada de enviar la información:",FuenteEntradaInfo )
    st.write('Dirección de la página web (si aplica):',DireccPagWeb )
    st.write('Medio de consulta o entrega de la información:',MedConsEntreInfo)
    st.write('Formato de la información:',FonrmatInfo)
    st.write('Observaciones consistencia: ',ObsConsis)
    st.write('Observaciones Exactitud semántica: ',ObsExactSemant)
    st.write('Observaciones Unicidad: ',ObsUnicidad)
    st.write('Observaciones Completitud',ObsComplet)
    st.write('Observaciones Exactitud Sintáctica: ',ObsExactSintact)
    st.write('Observaciones Dimensiones mínimas: ',ObsDimMin)
    st.write('Observaciones Actualidad: ',obsActualidad)
    st.write('Observaciones Confiabilidad: ',ObsConfiabilid)
    st.write('Número de registros inconsistentes: ',NumRegInconsistentes)
    st.write('Número de registros que carecen de exactitud semántica: ',NumRegsinExacSem)
    
    #indicadores provenientes del df


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Archivo '{file_path}' eliminado correctamente.")
    except FileNotFoundError:
        print(f"El archivo '{file_path}' no existe.")
    except PermissionError:
        print(f"No tienes permiso para eliminar el archivo '{file_path}'.")
    except Exception as e:
        print(f"Se produjo un error al eliminar el archivo '{file_path}': {e}")











def generar_grafica_estrellas(calificacion):
    # Definir los símbolos para cada fracción de estrella
    simbolos = {
        0: '☆',                # Estrella vacía
        0.2: '✫',              # Estrella rellena a un quinto
        0.4: '✬',              # Estrella rellena a dos quintos
        0.6: '✭',              # Estrella rellena a tres quintos
        0.8: '✮',              # Estrella rellena a cuatro quintos
        1: '★',                # Estrella llena
    }

    # Crear el símbolo de estrella basado en la calificación
    estrellas = ''
    for i in range(5):
        fraccion_estrella = round(calificacion - i, 2)  # Redondear a 2 decimales
        if fraccion_estrella >= 1:
            estrellas += simbolos[1]
        elif fraccion_estrella > 0:
            estrellas += simbolos[min(simbolos.keys(), key=lambda x: abs(x - fraccion_estrella))]
        else:
            estrellas += simbolos[0]

    # Devolver el símbolo de estrella como HTML
    return f'{estrellas}'




def add_rating_graph(df, column_name):
    # Verificar que la columna de calificaciones exista en el DataFrame
    if column_name not in df.columns:
        st.error(f"La columna '{column_name}' no existe en el DataFrame.")
        return df
    


def cantidad_duplicados_pandas(df, eje=0, numero=False, numero_filas=30000): # Funcion de duplucados para calidad de datos 
    """
    Retorna el porcentaje/número de filas o columnas duplicadas (repetidas) en el dataframe.

    :param df: (DataFrame de pandas) El DataFrame de pandas que se va a analizar.
    :param eje: (int) {1, 0} Valor por defecto: 0. Si el valor es `1` la validación se realiza por columnas.
                Si el valor es `0` la validación se realiza por filas.
    :param numero: (bool) {True, False} Valor por defecto: False. Si el valor es `False` el resultado se expresa como
                   un cociente, si el valor es `True` el valor se expresa como una cantidad de registros (número entero).
    :param numero_filas: (int) Valor por defecto: 30000. Número de filas que tendrá cada columna cuando se verifiquen
                         los duplicados por columna (cuando 'eje = 1'). Se utiliza para agilizar el proceso de verificación
                         de duplicados de columnas, el cual puede resultar extremadamente lento para un conjunto de datos
                         con muchas filas.
    :return: (int o float) Resultado de unicidad.
    """
    if not isinstance(numero, bool): # Verificacion que sea un numero booleano 0 o 1, si pone otro saldrá el error descrito en ValueError
        raise ValueError("'numero' debe ser booleano. {True, False}.")# Describe el error al no cumplirse la condicion del if de la linea anterior
    if eje not in [0, 1]: # condicional de validacion si no es 0 y 1 da error de ValueError
        raise ValueError("'eje' solo puede ser 0 o 1.")# Describe el error al no cumplirse la condicion del if de la linea anterior

    # Proporcion (decimal) de columnas repetidas
    if eje == 1:
        if df.shape[0] <= numero_filas:
            no_unic_columnas = df.T.duplicated()
        else:
            tercio = numero_filas // 3
            mitad = numero_filas // 2

            idx_mini = pd.Index(
                list(range(tercio)) + list(range(mitad, mitad + tercio)) + list(range(numero_filas - tercio, numero_filas))
            )

            no_unic_columnas = df.iloc[idx_mini].T.duplicated()

        if numero:
            cols = no_unic_columnas.sum()
        else:
            cols = no_unic_columnas.sum() / df.shape[1]

    # Proporción de filas repetidas
    else:
        no_unic_filas = df.duplicated()
        if numero:
            cols = no_unic_filas.sum()
        else:
            cols = no_unic_filas.sum() / df.shape[0]

    return cols


def valores_faltantes_dataframe(dataframe, numero=False):
    """
    Calcula el porcentaje/número de valores faltantes de cada columna del DataFrame.

    :param dataframe: DataFrame de Pandas. El DataFrame que se va a analizar.
    :param numero: (bool) {True, False} Valor por defecto: False. Si el valor es `False` el resultado se expresa como un cociente, si el valor es `True` el valor se expresa como una cantidad de registros (número entero).
    :return: Serie de pandas con la cantidad/cociente de valores faltantes de cada columna.
    """

    if not isinstance(dataframe, pd.DataFrame):
        #raise
        st.warning('olvidó cargar su set de datos, cargue su set de datos', icon="⚠️")
        return None

    if not isinstance(numero, bool):
        raise ValueError("'numero' debe ser booleano. {True, False}.")

    if numero:
        missing_columnas = pd.isnull(dataframe).sum()
    else:
        missing_columnas = pd.isnull(dataframe).sum() / len(dataframe)

    return missing_columnas



def calificacion_completitud(dataframe):
    """
    Calcula la fracción de valores faltantes totales en todo el DataFrame, dividida por el total de registros.

    :param dataframe: DataFrame de Pandas. El DataFrame que se va a analizar.
    :return: Fracción de valores faltantes totales en el DataFrame.
    """

    if not isinstance(dataframe, pd.DataFrame):
        #raise 
        st.warning('olvidó cargar su set de datos, cargue su set de datos', icon="⚠️")
        return None

    total_valores = dataframe.shape[0] * dataframe.shape[1]
    total_valores_faltantes = dataframe.isnull().sum().sum()

    fraccion_faltantes_totales = total_valores_faltantes / total_valores
    fraccion_completitud=1-fraccion_faltantes_totales

    ## cálculo de calificación de completitud

    calificacion_completitud = 5 * fraccion_completitud
    return calificacion_completitud



def tipo_columnas(df, tipoGeneral=True, tipoGeneralPython=True, tipoEspecifico=True):
    """
    Retorna el tipo de dato de cada columna del dataframe.

    :param df: DataFrame de pandas.
    :param tipoGeneral: (bool) {True, False}, valor por defecto: True.
        Incluye el tipo general de cada columna. Los tipos son: numérico,
        texto, booleano, otro.
    :param tipoGeneralPython: (bool) {True, False}, valor por defecto:
        True. Incluye el tipo general de cada columna dado por el método
        'pandas.dtypes' de Pandas
    :param tipoEspecifico: (bool) {True, False}, valor por defecto: True.
        Incluye el porcentaje de los tres tipos más frecuentes de cada
        columna. Se aplica la función nativa 'type' de Python para cada
        observación.

    :return: Dataframe de pandas con los tipos de dato de cada columna.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("'df' debe ser un DataFrame de pandas.")

    if not isinstance(tipoGeneral, bool):
        raise ValueError("'tipoGeneral' debe ser booleano. {True, False}")

    if not isinstance(tipoGeneralPython, bool):
        raise ValueError("'tipoGeneralPython' debe ser booleano. {True, False}")

    if not isinstance(tipoEspecifico, bool):
        raise ValueError("'tipoEspecifico' debe ser booleano. {True, False}")

    if not (tipoGeneral or tipoGeneralPython or tipoEspecifico):
        raise ValueError("Al menos uno de los parámetros tipoGeneral, tipoGeneralPython o tipoEspecifico debe ser True")

    lista_nombres = df.columns
    tipos_dtypes = df.dtypes.apply(str)
    tipo_datos = dict()

    # Tipo general en español
    if tipoGeneral:
        dic_tipo = {
            "int": "Numérico",
            "float": "Numérico",
            "str": "Texto",
            "bool": "Booleano",
            "datetime64[ns]": "Fecha",
            "object": "Otro",
        }
        general = [dic_tipo.get(tipo, "Otro") for tipo in tipos_dtypes]
        tipo_datos["tipo_general"] = general

    # Tipo general de Python
    if tipoGeneralPython:
        tipo_datos["tipo_general_python"] = tipos_dtypes.tolist()

    # Tipo específico Python
    if tipoEspecifico:
        temp_list = []
        for columna in lista_nombres:
            tip = df[columna].apply(type).value_counts(normalize=True, dropna=False)

            nombre_tipo = [
                re.findall("'(.*)'", str(t))[0] for t in tip.index.tolist()
            ]

            temp_dic = {}
            for i, (nom, t) in enumerate(zip(nombre_tipo, tip)):
                key = f"tipo_especifico_{i + 1}"
                temp_dic[key] = [f"'{nom}': {round(t*100,2)}%"]
            temp_list.append(temp_dic)

        max_keys = max(temp_list, key=len).keys()
        for d in temp_list:
            for key in max_keys:
                if key not in d:
                    d[key] = [""]

            for k, v in d.items():
                if k in tipo_datos:
                    tipo_datos[k].extend(v)
                else:
                    tipo_datos[k] = v

    tips = pd.DataFrame.from_dict(tipo_datos, orient="index", columns=lista_nombres).T

    return tips


def f_calificacion_calidad_datos(df_):

    if df_ is None or df_.empty:

        #print("El DataFrame está vacío o es None.")
        return None 

    ### Dimension de completitud
    ## calificaicon completitud
    cal_complet=calificacion_completitud(df)

    ### Dimension de unicidad
    ## calificacion unicidad
    # unicidad columnas calificacion
    fraccion_dupl_col=cantidad_duplicados_pandas(df, eje=1, numero=False, numero_filas=30000)
    fraccion_unicidad_col=1-fraccion_dupl_col
    calificacion_unicid_col=fraccion_unicidad_col*5

    # calificacion unicidad filas
    fraccion_depl_filas=cantidad_duplicados_pandas(df, eje=0, numero=False, numero_filas=30000)
    fraccion_unicidad_fil= 1-fraccion_depl_filas
    calificacion_unicid_fil=fraccion_unicidad_fil*5

    #calificacion gobal unicidad
    calificacion_global_unicidad= (calificacion_unicid_fil+calificacion_unicid_col)/2
    
    ###Dimension exactitud
    df_tipos=tipo_columnas(df, tipoGeneral=True, tipoGeneralPython=True, tipoEspecifico=True)
    df_tipos['calificacion_exactitud_col'] = (df_tipos['tipo_especifico_1'].apply(lambda x: float(re.findall(r"[-+]?\d*\.\d+|\d+", x)[0])) / 100)*5
    calificacion_exactitud = df_tipos['calificacion_exactitud_col'].mean()

    ###Dimensiones minimas
        # Dimensión de precisión

    ## Calculo de minimo de filas
    minima_cant_filas = df.shape[0] / 50

    # Verificamos si minima_cant_filas es mayor que 1
    if minima_cant_filas > 1:
        frac_min_cant_filas = 1
    else:
        frac_min_cant_filas = 0

    ## Cálculo de minimo de columnas

    minima_cant_colum = df.shape[1] / 3

    # Verificamos si minima_cant_filas es mayor que 1
    if minima_cant_colum > 1:
        frac_min_cant_col = 1
    else:
        frac_min_cant_col = 0

    ## Fracción de dimensión minima

    media_fracciones_min_dim_df = (frac_min_cant_filas + frac_min_cant_col) / 2

    # Cálculo de calificación de dimensión mínima

    calificacion_dim_min_df = 5 * media_fracciones_min_dim_df

    ### Calificación total
    calificacion_total_df = (calificacion_global_unicidad + cal_complet + calificacion_exactitud + calificacion_dim_min_df) / 4

    ## creando DF de calificaciones y Total

    df_calificaciones_calidad = {'Dimensiones de calidad': ['Unicidad',
                                                            'Completitud',
                                                            'Exactitud',  
                                                            'Dimensiones minimas',
                                                            'Total'],
                                 'Calificaciones': [calificacion_global_unicidad,
                                                    cal_complet,
                                                    calificacion_exactitud,
                                                    calificacion_dim_min_df,
                                                    calificacion_total_df]
                                 }

    df_calificaciones_calidad = pd.DataFrame(df_calificaciones_calidad)

    ## agregando columna de salida gráfica de estrellas por calificación

    # Agregar una columna con las gráficas de estrellas
    df_calificaciones_calidad['Gráfica calificación'] = df_calificaciones_calidad['Calificaciones'].apply(generar_grafica_estrellas)
    #df_calificaciones_calidad = add_rating_graph(df_calificaciones_calidad, 'Calificaciones')
    # creando tabla HTML

    tabla_html = df_calificaciones_calidad.to_html(index=False)


    # Retornar un diccionario con los DataFrames y la tabla HTML
    return tabla_html, df_calificaciones_calidad,calificacion_global_unicidad,cal_complet, calificacion_exactitud, calificacion_dim_min_df, calificacion_total_df





#1.1. f_cargar_archivo: función permite identificar el tipo de archivo cargado y permite leerlo.




def download_profile(profile, output_file="profile_report.html"):
    profile.to_file(output_file)
    with open(output_file, "rb") as file:
        profile_bytes = file.read()
    return profile_bytes




def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Archivo '{file_path}' eliminado correctamente.")
    except FileNotFoundError:
        print(f"El archivo '{file_path}' no existe.")
    except PermissionError:
        print(f"No tienes permiso para eliminar el archivo '{file_path}'.")
    except Exception as e:
        print(f"Se produjo un error al eliminar el archivo '{file_path}': {e}")


# Function to save profile report
def save_profile_report(profile, folder_path):
    profile_path = folder_path + "/profile_report.html"
    profile.to_file(profile_path)
    st.success(f"Profile report saved successfully at {profile_path}")


    


# def f_cargar_archivo(uploaded_file): 
#     # Se obtiene la extensión del archivo cargado
#     extension = uploaded_file.name.split(".")[-1].lower()

#     #Condicionales para verificar el tipo de archivo y cargar los datos según corresponda
#     if extension == "csv":
#         df = pd.read_csv(uploaded_file)
#     elif extension == "xlsx" or extension == "xls":
#         df = pd.read_excel(uploaded_file)
#     elif extension == "txt":
#         df = pd.read_csv(uploaded_file, delimiter="\t")  # Puedes ajustar el delimitador según sea necesario

#     # si el archivo no se ajusta a ningún formato CSV, EXCEL O TXT se devuelve un mensaje.
#     else:
#         #raise
#         #ValueError(f"Formato de archivo no compatible: {extension}. Solo se admiten archivos CSV, Excel o TXT.")
#         st.warning('olvidó cargar su set de datos, cargue su set de datos', icon="⚠️")
#         return None

#     return df


def f_cargar_archivo(uploaded_file):
    """
    Intenta cargar y leer un archivo en formato CSV, Excel o TXT, 
    con manejo avanzado para CSV incluyendo múltiples delimitadores y codificaciones.
    
    Parámetros:
    - uploaded_file: Un objeto file-like o la ruta a un archivo.
    
    Retorna:
    - Un DataFrame de pandas con los datos del archivo, o None si el archivo no es compatible.
    """
    # Se obtiene la extensión del archivo cargado
    extension = uploaded_file.name.split(".")[-1].lower() if hasattr(uploaded_file, 'name') else uploaded_file.split(".")[-1].lower()
    
    # Codificaciones y delimitadores para archivos CSV
    codificaciones = ['utf-8', 'iso-8859-1', 'windows-1252']
    delimitadores = [',', ';']

    try:
        if extension == "csv":
            # Intenta diferentes combinaciones de delimitadores y codificaciones
            for encoding in codificaciones:
                for delimiter in delimitadores:
                    # Rebobinar el archivo antes de cada lectura
                    uploaded_file.seek(0)
                    try:
                        df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding)
                        if df.shape[1] > 1:
                            print(f"Archivo CSV leído correctamente con delimitador '{delimiter}' y codificación '{encoding}'.")
                            return df
                    except Exception:
                        continue
            st.warning("No se pudo leer el archivo CSV con las combinaciones probadas.", icon="⚠️")
            return None
        elif extension in ["xlsx", "xls"]:
            uploaded_file.seek(0)  # Rebobinar para leer el archivo Excel
            return pd.read_excel(uploaded_file)
        elif extension == "txt":
            uploaded_file.seek(0)  # Rebobinar para leer el archivo TXT
            return pd.read_csv(uploaded_file, delimiter="\t")
        else:
            st.warning('Formato de archivo no compatible. Solo se admiten archivos CSV, Excel o TXT.', icon="⚠️")
            return None
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}", icon="⚠️")
        return None



# 1.2.f_exportar_perfil: esta función permite exportar profiles elaborados en pandas profile en diferentes formatos como JSON, HTML y PDF
def f_exportar_perfil(profile, formato):
    # Se utiliza try-except para manejar posibles errores al exportar el perfil
    try:
        # Determinar el formato de exportación
        if formato == 'PDF':
            # Exportar el perfil a PDF
            profile.to_file("perfil_reporte.pdf")
            st.success("El perfil ha sido exportado exitosamente en formato PDF como 'perfil_reporte.pdf'")
        elif formato == 'HTML':
            # Exportar el perfil a HTML
            profile.to_file("perfil_reporte.html")
            st.success("El perfil ha sido exportado exitosamente en formato HTML como 'perfil_reporte.html'")
        elif formato == 'JSON':
            # Exportar el perfil a JSON
            profile.to_file("perfil_reporte.json")
            st.success("El perfil ha sido exportado exitosamente en formato JSON como 'perfil_reporte.json'")
        else:
            st.error("Formato de exportación no válido. Por favor, seleccione PDF, HTML o JSON.")
    except Exception as e:
        st.error(f"Ocurrió un error al exportar el perfil: {e}")



def save_to_zip(file_names, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as z:
        for file in file_names:
            z.write(file, os.path.basename(file))
    return zip_name

# Define la función de reinicio fuera de cualquier bloque condicional para evitar problemas de alcance
def reset_app():
    # Limpiar todas las claves del estado de la sesión
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()  # Forzar un rerun de la aplicación
        
#------------------------
#2. configurando la disposición de la página
#hay mas modos como:
# Centered: Coloca el contenido en el centro de la página.
# Narrow: Un diseño más estrecho que wide.
# Wide: Un diseño amplio (el que ya conoces).
# Fullscreen: Muestra la aplicación en pantalla completa, eliminando cualquier barra de desplazamiento o interfaz del navegador.

st.set_page_config(layout='wide') 	
#------------------------
#3. Añadiendo logo
logo = Image.open(r'Min_justicia.png')	
st.sidebar.image(logo,  width=300)

#-------------------------
#4. Añadiendo expander 
# se añado un expander dentro de una sidebar, es decir la barra que se despliega de izquierda a derecha	
# Cuando se utiliza with, Python se asegura de que los recursos asociados con el expander
# se liberen adecuadamente una vez que el bloque with termine de ejecutarse. 
# En el caso de st.sidebar.expander, esto podría incluir la liberación de memoria
# o la eliminación del expander de la barra lateral.
# En resumen, el uso de with garantiza una gestión adecuada
# de los recursos asociados con el expander

st.sidebar.write("""	
    **Descripción App:**

Esta aplicación proporciona una plataforma integral para el análisis exploratorio de datos, permitiendo la carga de archivos en diversos formatos como Excel y CSV.
Los usuarios pueden elegir entre dos modos de análisis: un modo mínimo, recomendado para evaluaciones rápidas, y un modo completo, que permite una exploración más profunda de correlaciones e interacciones entre variables.
Además, la herramienta evalúa y califica cada dimensión de la calidad de los datos según criterios establecidos en diversas normativas, incluyendo ISO 25000, DAMA, el manual de calidad de datos de MINTIC y la guía de atributos
de calidad de datos del Ministerio de Justicia y del Derecho, asegurando así un manejo riguroso y conforme a estándares reconocidos en la gestión de datos.
""")




#4. Agregando un titulo al estilo CSS 
     
#st.markdown(): Esta función permite mostrar texto formateado con Markdown dentro de la interfaz de Streamlit
#""": Al usar tres comillas dobles, se indica que el código dentro es un string multi-línea, lo cual es útil para escribir el código CSS sin problemas de sangrado.
#<style>: Esta etiqueta HTML inicia un bloque de código CSS que define estilos para elementos.
# .font: Esto define un clase CSS llamada "font" que aplicará los estilos definidos a cualquier elemento con dicha clase.
# font-size: 30px: Establece el tamaño de la fuente a 30 píxeles.
# font-family: 'Cooper Black': Establece la fuente a "Cooper Black", se puede personalizar por otros tipos de letra
# color: #FF9633: Define el color del texto con un código hexadecimal
#unsafe_allow_html=True dentro de la función st.markdown() tiene un rol crucial al permitir la interpretación de código HTML dentro del markdown que se está 
#mostrando. Sin esta configuración, el código HTML se interpretaría como texto plano y no se ejecutaría.

# st.markdown(""" <style> .font {                                          	
#     font-size:30px ; font-family: 'Cooper Black'; color: #FF9633;} 	
#     </style> """, unsafe_allow_html=True)	

#st.markdown(): Esta función permite mostrar texto formateado con Markdown dentro de la interfaz de Streamlit
#<p>: Esta etiqueta HTML crea un párrafo.
# class="font": Aquí se asigna la clase "font" al párrafo, de forma que heredará los estilos definidos anteriormente.
# Import your data and generate a Pandas data profiling report easily...</p>: Este es el texto que se visualizará dentro del párrafo con los estilos aplicados
#unsafe_allow_html=True dentro de la función st.markdown() tiene un rol crucial al permitir la interpretación de código HTML dentro del markdown que se está 
#mostrando. Sin esta configuración, el código HTML se interpretaría como texto plano y no se ejecutaría.

# st.markdown('<p class="font">Import your data and generate a Pandas data profiling report easily...</p>', unsafe_allow_html=True)

#### EJEMPLO DE COMO PONER DOS LINEAS DE TEXTO CON DIFERENTE FORMATO
     


st.markdown("""
    <style>
        .font {
            font-size: 30px;
            font-family: 'Cooper Black';
            color: #FF9633;
        }
        .font2 {
            font-size: 30px;
            font-family: 'Cooper Black';
            color: #007BFF; /* Cambia el color aquí */
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('''
    <h1 style="color: black; font-size: 40px; font-weight: bold;">Subdirección de Gestión de Información en Justicia</h1>
    <h2 style="color: black; font-size: 30px; font-weight: bold;">Evalue la calidad de los datos</h2>
''', unsafe_allow_html=True)

with st.sidebar.expander("Instructivo"):
    st.write('''
Para utilizar esta herramienta, siga los pasos descritos para cada módulo:

**Módulo de carga de archivos**
             
Aquí es donde se cargan los datos, asegúrese de que sus archivos estén en formato .xlsx o .csv (separados por comas). Note que el aplicativo no acepta archivos CSV separados por punto y coma ni archivos en formato .XLS. Para cargar el archivo a analizar siga los sigueintes pasos:
1. De clic en browse files.
2. Seleccione el archivo a cargar desde la ubicación de almacenamiento en su computador.
3. Cargue el archivo.

**Módulo de selección de columnas**
             
Aquí es donde selecciona las columnas con las cuales quiere trabajar el análisis o en su defecto el total de columnas.
1. Elija trabajar con todas las columnas de su conjunto de datos o seleccione solo un subconjunto. Las opciones disponibles son "Todas las columnas" o "Subconjunto de columnas".
2. Si selecciona trabajar con un subconjunto de columnas, debe seleccionar las columnas con las que quiere trabajar.

**Modo de Análisis**
             
Este módulo ofrece dos enfoques de análisis mediante el paquete `pandas-profile`. Al seleccionar el modo mínimo, obtendrá un análisis exploratorio básico que incluye un resumen de características clave, como columnas numéricas y categóricas, el porcentaje de datos faltantes del conjunto total, y el promedio de tamaño en memoria del conjunto de datos. Para cada variable, se proporcionan estadísticas detalladas como el número de valores únicos, datos faltantes, frecuencia de valores categóricos y diversas alertas relacionadas con posibles desbalances, datos perdidos, o datos que podrían requerir limpieza.

Si opta por el análisis completo, encontrará todo lo mencionado anteriormente, pero con un análisis adicional que explora las relaciones entre variables, incluyendo la detección de correlaciones potenciales entre ellas.
Siga los siguientes pasos para obtener el análisis que seleccione:

1.	Seleccionar el tipo de análisis que quiere explorar, ya sea completo o mínimo.
2.	Presione el botón generar reporte
             
**Módulo de Formulario de Informe de Inspección y Análisis**
                        
Este módulo contiene un formulario que debe completar con la información básica del conjunto de datos analizado anteriormente. En este formulario, tendrá la oportunidad de comentar sobre diversas dimensiones de calidad de datos, incluyendo consistencia, exactitud semántica, exactitud sintáctica, completitud, unicidad, y actualidad. Además, deberá indicar la cantidad de datos que considere inconsistentes y aquellos que carezcan de exactitud semántica dentro de su conjunto de datos. Para completar este módulo, siga los pasos a continuación:

**poner definiciones de dimensiones de calidad con ejemplo**
1. Complete el formulario con los datos requeridos.
2. Haga clic en el botón "Guardar formulario".

Una vez finalizado, se generará un resumen de los datos guardados y se mostrará una tabla que incluye los comentarios ingresados y la calificación de cada dimensión de calidad de datos.

**Módulo de descarga**
             
Finalmente, el módulo de descarga se activará una vez que haya completado y guardado el formulario. Al hacer clic en el botón de descarga, se generará un archivo ZIP que incluye el análisis realizado por el paquete `pandas-profile` en formato .html, así como el informe de inspección y análisis en formato .pdf.

    ''')

# Configuración del tamaño máximo de mensaje a 1 GB
maxMessageSize = 2000



### alternativa para que reciba mas tipos de archivos diferentes al CSV 
uploaded_file = st.file_uploader("Cargar archivo:", type=['csv', 'xlsx'])

if uploaded_file is not None:	#comprueba si el usuario ha cargado un archivo
#    df=pd.read_csv(uploaded_file)	# lee el archivo en formato csv 
    
    #st.session_state['uploaded_file'] = uploaded_file  
    df = f_cargar_archivo(uploaded_file)
    file_name = uploaded_file.name 
    

    num_columns = df.shape[1]
    num_rows = df.shape[0]
    total_reg_df=num_rows*num_columns



#---------------- 
else:
    #uploaded_file = st.session_state.get('uploaded_file')
    if uploaded_file is not None:
        file_name = uploaded_file.name
        df = f_cargar_archivo(uploaded_file)
        file_name = uploaded_file.name
    else:
        df = None
if df is not None:
    if 'current_option1' not in st.session_state:
        st.session_state['current_option1'] = None

    option1=st.sidebar.radio(	
     '¿Qué columnas desea incluir en el informe?',	
     ('Todas las columnas', 'Un subconjuto de columnas'))	  # da el nombre a las opciones radio que se pongan, aqui se pone el número de n opciones que puede tomar el radio, hay que tener cuidado porque el condicional de las opciones debe llevar estos mismos nombres para que sirva
    
    # Verifica si el valor de option1 ha cambiado
    if st.session_state['current_option1'] is not None and st.session_state['current_option1'] != option1:
        if 'submitted' in st.session_state:
            del st.session_state['submitted']  # Elimina el indicador de formulario enviado
            st.experimental_rerun()  # Reinicia la aplicación para reflejar el cambio

    # Actualiza el valor actual de option1 en el estado de sesión
    st.session_state['current_option1'] = option1
    
    if option1=='Todas las columnas': # como se observa en esta linea el condicional de la opcion 1 tiene el mismo nombre que en la linea de arriba, así debe ser para que funcione. 
        df=df	# n este caso, no se modifica el DataFrame df ya que se quieren analizar todas las variables del archivo
    	
    elif option1=='Un subconjuto de columnas':	# en esta linea se establece una segunda condicion para la opcion 1, recordar que se llama igual a como se dejó arriba en el boton de radio
        var_list=list(df.columns)	# se crea una lista con todas las columnas del DataFrame
        option3=st.sidebar.multiselect(	
            'Seleccione las variables que quiera incluir en el análisis',	
            var_list)	# Esta función de Streamlit crea un widget de selección múltiple dentro de la barra lateral ".sidebar" es para asignar lo que sea a una barra lateral, el ".multiselect" crea un multiselector
                        #normalmente el multiselector recibe dentro de su estructura ("label", "opciones"). el label en este caso es 'Seleccione las variables que quiera incluir en el análisis',
                        #Las opciones son var_list, que es una lista que proviene de los nombre de las columnas del df de entrada, lo cual se saca con list(df.columns)
        #df=df[option3]  # esta parte es la que realmente hace que la función de seleccionar haga algo en el df, sin esto simplemente se ve en el multiselector las opciones seleccionadas sin alterar el df
                        # se observa que lo que uno escoja de la lista con el multislector va a quedar guardado en la variable option3 que a su vez en esta linea "df=df[option3]",
                        # se carga en la seleccion de columnas del df
        if option3:  # Verifica si se seleccionaron columnas
            df = df[option3]
            # Llama a la función de calificación solo si hay columnas seleccionadas
            tabla_html, df_calificaciones_calidad, calificacion_global_unicidad, cal_complet, calificacion_exactitud, calificacion_dim_min_df, calificacion_total_df = f_calificacion_calidad_datos(df)
        else:
            st.sidebar.error("Debe seleccionar al menos una columna para continuar con el análisis.")
            # df = None  # Asegura que no se proceda con un DataFrame no configurado
            # st.error("No hay datos para mostrar. Por favor selecciona las columnas necesarias.")


    #8. Creando condicional selector selectorbox para el analisis minimo o completo que propone en los siguientes condiocionales usando AgrGrid
    
    # en el caso de option2 es importante recordar la estructura ('label',( 'opc1','opc2'))
    option2 = st.sidebar.selectbox(	
     'Escoger el modo de análisis:',	
     ('Mínimo', 'Completo'))	
    
    # perimer condicional que dá como resultado la ejecución de la selección de la opción 'Complete Mode'
    if option2=='Completo':	
        mode='Completo'	
        st.sidebar.warning('''El modo completo contempla análisis y cálculos adicionales que incluyen una tabla de correlación entre las variables de objeto de análisis y un mapa de calor de correlación.
                            Además, se realiza un análisis exploratorio con recomendaciones para cada variable.
                            Este modo requiere un mayor gasto computacional. Si no es necesario evaluar las correlaciones entre las variables, se recomienda optar por el módulo mínimo.''')	
    
        pass
    elif option2=='Mínimo': # si se selecciona minimal mode, en la variable mode se selecciana 'minimal	
        mode='minimal'	
        st.sidebar.warning('''El modo mínimo predeterminado desactiva calculos adicionales, como correlaciones y detección de filas duplicadas.
                            Cambiar al modo completo puede hacer que la aplicación génere mayor gasto computacional, depende del tamaño del conjunto de datos.''')	
    else:
        st.error("El modo de análisis no está definido. Por favor, selecciona un modo de análisis.")

#9. Se crea un objero AgGrid llamado grid_response
# grid_response: esta variable contiene información sobre la cuadrícula, incluyendo los datos actualizados por el usuario
    grid_response = AgGrid(	
        df,	# aquí va el df del cual se están domando los datos
        editable=True, #Este parámetro indica que la cuadrícula AG-Grid será editable. Esto significa que los usuarios pueden editar los valores directamente en la cuadrícula si así lo desean
        height=300, #la altura de la cuadrícula AG-Grid en píxeles
        width='100%', #Este parámetro establece el ancho de la cuadrícula AG-Grid
        )	
    updated = grid_response['data']	# extrae los datos actualizados de la cuadrícula AG-Grid
    df1 = pd.DataFrame(updated) # crea un nuevo dataframe con los datos actualizados
  
# 10. Se crea un boton con un label "Generate Report", si el usuario ejecuta le botón ejecuta el código if o el elif, todo depende de la condición que se cumpla,
# darse cuenta de la sintaxis despues de los ":"  
#if st.button('Generar Reporte'):
if button("Generar Reporte", key="generate_report"):
    #st.session_state['generate_report'] = True
# aplicando funcion de calificación
    resultado = f_calificacion_calidad_datos(df)
    if resultado is not None:
    
        ##generar tabla reporte con calificaciones 
        tabla_html, df_calificaciones_calidad,calificacion_global_unicidad,cal_complet, calificacion_exactitud, calificacion_dim_min_df, calificacion_total_df=f_calificacion_calidad_datos(df)
        #st.write(df_calificaciones_calidad)
    else:
        #st.error("No se generaron datos. El DataFrame puede estar vacío o ser None.")
        st.warning('olvidó cargar su set de datos, cargue su set de datos', icon="⚠️")
        time.sleep(3)
        reset_app()
        

    #st.markdown(tabla_html, unsafe_allow_html=True)
# 10.1. primer condicional, el objetivo es hacer un analisis completo 
    # En el analisis completo hay un error porque si ud modifica los datos en este caso no se va a ver afectado el df de objeto de analisis, por eso se modificó a df1
    #if mode=='complete':
    
    if mode == 'Completo':
            # se crea la variable profile, con el eda que saca la función ProfileReport
            # al parecer el modo complete viene por defecto en el EDA, por lo que en este bloque de código no se hace un enfasis en este parametro
            profile=ProfileReport( # ProfileReport, es una función que permite hacer un analisis exploratorio EDA  a partir de un dataframe de pandas, contiene los siguientes parámetros:
                df1, # df del que provienen los datos
                title="User uploaded table", #título del reporte
                progress_bar=True #  Indica si se debe mostrar una barra de progreso durante la generación del reporte

            ) 
            st_profile_report(profile) #se utiliza para mostrar un reporte de análisis exploratorio de datos (EDA) generado por la librería pandas-profiling en la interfaz de Streamlit
                                    #De eliminarse esta línea o no correrse, simplemente la aplicación no mostrará ningún EDA, ni siquierea la progress_bar
            st.session_state['profile'] = profile
            
            if 'generate_report' in st.session_state:        
                    # PONER AQUI EL FORMULARIO
                    with st.form("my_form"):
                        st.title("Formulario Informe de Inspección y Análisis")

                        # Campos de entrada de texto

                        # 1. Encargado del MJD EncargadoMJD

                        EncargadoMJD = st.text_input("Encargado de diligenciar el formato (MJD): ")
                    

                        # 2. ÁreaEncargadoMJD area encargada
                        AreaEncargadoMJD = st.text_input("Área del encargado de diligenciar el formato (MJD):")

                        # 3. Fecha de recepcion o extracción
                        FechaRecepExtrac = st.date_input("Fecha de recepción o extracción:", 
                                                            min_value=datetime(2000, 1, 1), 
                                                            max_value=datetime(2100, 1, 1))
                        FechaRecepExtrac=str(FechaRecepExtrac)




                        st.markdown("Periodo del reporte: ")
                        default_start, default_end = datetime.now() - timedelta(days=1), datetime.now()
                        refresh_value = timedelta(days=1)
                        date_range_string = date_range_picker(picker_type=PickerType.date,
                                                            start=default_start, end=default_end,
                                                            key='date_range_picker',
                                                            refresh_button={'is_show': True, 'button_name': 'Refresh Last 1 Days',
                                                                            'refresh_value': refresh_value})
                        if date_range_string:
                            start, end = date_range_string
                            st.write(f"Date Range Picker [{start}, {end}]")
                            # Suponiendo que start y end son objetos datetime
                            #start_str = start.strftime("%Y-%m-%d")  # Formato de cadena: YYYY-MM-DD
                            #end_str = end.strftime("%Y-%m-%d")  # Formato de cadena: YYYY-MM-DD
                            start_str = str(start)
                            end_str = str(end)


                            # Usar las cadenas en lugar de los objetos datetime
                            #st.write(f"Desde {start_str} hasta {end_str}")
                            date_range_str_out = f"Desde {start_str} hasta {end_str}"

                        
                        # Periodo de actualización 
                        
                        PeriodoActInfo=st.selectbox("Periodicidad de actualización de la información: ", ["Diaria", "Semanal", "Quincenal","Mensual","Bimensual","Trimestral", "Cuatrimestral","Semestral" ,"Anual","Por demanda"])
                            # NombreArchivo        
                        #NombreArchivo=st.write(f"Nombre del archivo cargado: {file_name}")
                        
                        NombreArchivo='archivo'
                        # Tipo de Fuente
                        TipoFuenteInfo= st.selectbox("Tipo de la fuente de información: ", ["Interna", "Externa"])
                        # EntidadesFuenteInfo
                        EntidadesFuenteInfo = st.text_input("Entidad(es) de la fuente de la información:")
                        # contactoEncargadoInfo
                        contactoEncargadoInfo=st.text_input("Contacto encargado de enviar la información:")
                        # dependencia encargado de enviar la informacion
                        DirecEncargadoInfo = st.text_input("Dependencia encargada de enviar la información:")
                        # FuenteEntradaInfo
                        FuenteEntradaInfo=st.selectbox("Fuente de entrada de información:", ["Acuerdo Formal", "Acuerdo no Formal","Datos Sistemas de Información Internos"])
                        # DireccPagWeb
                        DireccPagWeb=st.text_input('Dirección de la página web (si aplica):')
                        # MedConsEntreInfo
                        MedConsEntreInfo=st.selectbox('Medio de consulta o entrega de la información:',["Oficios","Correos electronicos","Web Services","Servidor de Archivos SFTP","Carpeta Compartida","Otros","No Aplica"])
                        #Formato fuente de información
                        FonrmatInfo= st.selectbox('Formato de la información:', ["Excel","Word","Pdf","Pptx","Web","Txt","Base de Datos","Archivo Plano-CSV","Formulario Web","Web Api"])
                        # Observaciones consistencia
                        ObsConsis=st.text_input("Observaciones consistencia:")
                        #ObsExactSemant exactitud
                        ObsExactSemant=st.text_input("Observaciones Exactitud semántica:")
                        # 'Observaciones Unicidad',ObsUnicidad
                        ObsUnicidad=st.text_input('Observaciones Unicidad:')
                        # ObsComplet 
                        ObsComplet=st.text_input('Observaciones Completitud:')
                        # ('Observaciones Exactitud Sintáctica',)
                        ObsExactSintact=st.text_input('Observaciones Exactitud Sintáctica:')
                        # 'Observaciones Dimensiones mínimas',
                        ObsDimMin=st.text_input('Observaciones Dimensiones mínimas:')
                        # st.write('Observaciones Actualidad',)
                        obsActualidad=st.text_input('Observaciones Actualidad:')
                        #('Observaciones Confiabilidad',)
                        ObsConfiabilid=st.text_input('Observaciones Confiabilidad:')
                        
                        #Cantidad de registros inconsistentes en el df
                        
                        NumRegInconsistentes = st.number_input("Ingrese la cantidad de registros inconsistentes:",step=1,max_value=total_reg_df)
                        
                        #cantidad de registros que carecen de exactitud semántica
                        NumRegsinExacSem= st.number_input("Ingrese la cantidad de registros que carecen de exactitud semántica:",step=1,max_value=total_reg_df)
                        # Botón para enviar el formulario
                        submitted = st.form_submit_button("Guardar Formulario")
                        

                        
                        if submitted:
                            try:
                                st.session_state['submitted'] = True
                                    # Verificar si el campo EncargadoMJD está vacío
                                
                                guardar_datos(EncargadoMJD, AreaEncargadoMJD, FechaRecepExtrac, date_range_str_out, PeriodoActInfo,NombreArchivo,TipoFuenteInfo, EntidadesFuenteInfo,
                                            contactoEncargadoInfo, DirecEncargadoInfo, FuenteEntradaInfo, DireccPagWeb, MedConsEntreInfo, FonrmatInfo,ObsConsis, ObsExactSemant,ObsUnicidad,ObsComplet,
                                            ObsExactSintact, ObsDimMin
                                            ,obsActualidad, ObsConfiabilid,NumRegInconsistentes,NumRegsinExacSem)

                                    # Nombre del archivo PDF a generar
                                nombre_archivo = "informe_test.pdf"

                                info_general = {
                                "Encargado de diligenciar el formato (MJD):":EncargadoMJD,
                                "Área del encargado de diligenciar el formato (MJD):":AreaEncargadoMJD,
                                "Fecha de recepción o de extracción:":FechaRecepExtrac,
                                "Periodo del reporte:":date_range_str_out,
                                "Periodicidad de actualización de la información:":PeriodoActInfo,
                                "Nombre del archivo:":NombreArchivo,
                                "Tipo de la fuente de información:":TipoFuenteInfo,
                                "Entidad(es) de la fuente de la información:":EntidadesFuenteInfo,
                                "Contacto encargado de enviar la información:":contactoEncargadoInfo,
                                "Dependencia encargada de enviar la información:":DirecEncargadoInfo,
                                "Fuente de entrada de la información:":FuenteEntradaInfo,
                                "Dirección de la página web (si aplica):":DireccPagWeb,
                                "Medio de consulta o entrega de la información:":MedConsEntreInfo,
                                'Formato de la información:':FonrmatInfo}
                                
                                

                                            
                                calificacion_global_unicidad_str = str(calificacion_global_unicidad)
                                cal_complet_str = str(cal_complet)
                                calificacion_exactitud_str = str(calificacion_exactitud)
                                calificacion_dim_min_df_str = str(calificacion_dim_min_df)
                                calificacion_total_df_str = str(calificacion_total_df)

                                # #calificación de consistencia
                                
                                calificacion_consistencia=((total_reg_df-NumRegInconsistentes)/total_reg_df)*5
                
                                # # Calificación exactitud semantica
                                
                                calificacion_exactitud_semantica=((total_reg_df-NumRegInconsistentes)/total_reg_df)*5

                                tabla_cuantitativa = {
                                0:["Exactitud semántica", calificacion_exactitud, ObsExactSemant],
                                1:["Unicidad", calificacion_global_unicidad, ObsUnicidad],
                                2:["Completitud", cal_complet, ObsComplet],
                                3:["Exactitud (Exactitud sintáctica)",calificacion_exactitud_semantica , ObsExactSintact],
                                4:["Dimensiones mínimas", calificacion_dim_min_df, ObsDimMin],
                                5:["Consistencia", calificacion_consistencia,ObsConsis]}

                                tabla_cualitativa = {
                                0:["Actualidad", "Todo es actual"],
                                1:["Confiabilidad","Todo es confiable"]}
                                # #calificación de consistencia
                                
                                calificacion_consistencia=((total_reg_df-NumRegInconsistentes)/total_reg_df)*5
                
                                # # Calificación exactitud semantica
                                
                                calificacion_exactitud_semantica=((total_reg_df-NumRegInconsistentes)/total_reg_df)*5

                                tabla_cuantitativa = {
                                0:["Exactitud semántica", calificacion_exactitud, ObsExactSemant],
                                1:["Unicidad", calificacion_global_unicidad, ObsUnicidad],
                                2:["Completitud", cal_complet, ObsComplet],
                                3:["Exactitud (Exactitud sintáctica)",calificacion_exactitud_semantica , ObsExactSintact],
                                4:["Dimensiones mínimas", calificacion_dim_min_df, ObsDimMin],
                                5:["Consistencia", calificacion_consistencia,ObsConsis]}
                                total_calif_todas_dim=(calificacion_exactitud+calificacion_global_unicidad+cal_complet+calificacion_exactitud_semantica+calificacion_dim_min_df+calificacion_consistencia)/6

                                tabla_cuantitativa_para_df = {
                                0:["Exactitud semántica", calificacion_exactitud, ObsExactSemant],
                                1:["Unicidad", calificacion_global_unicidad, ObsUnicidad],
                                2:["Completitud", cal_complet, ObsComplet],
                                3:["Exactitud (Exactitud sintáctica)",calificacion_exactitud_semantica , ObsExactSintact],
                                4:["Dimensiones mínimas", calificacion_dim_min_df, ObsDimMin],
                                5:["Consistencia", calificacion_consistencia,ObsConsis],
                                6:["Total", total_calif_todas_dim,'']}
                                df_calificaciones = pd.DataFrame.from_dict(tabla_cuantitativa_para_df, orient='index', columns=['Categoría', 'Calificación', 'Observaciones'])
                                df_calificaciones['Gráfica calificación'] = df_calificaciones['Calificación'].apply(generar_grafica_estrellas)
                                #df_calificaciones = df_calificaciones[['Categoría', 'Calificación', 'Gráfica Calificación', 'Observaciones']]


                                tabla_cualitativa = {
                                0:["Actualidad", "Todo es actual"],
                                1:["Confiabilidad","Todo es confiable"]}

                                file_pdf=generar_pdf(nombre_archivo, info_general, tabla_cuantitativa, tabla_cualitativa)

                                st.write(df_calificaciones)
                            except:
                                print('error')
                                st.error('This is an error', icon="🚨")


                    if 'profile' in st.session_state and 'submitted' in st.session_state:
                            try:

                                file = download_profile(profile, output_file="profile_report.html")
                                file_list = ['informe_test.pdf', 'profile_report.html']
                                zip_output_name = 'informe_calidad_informacion.zip'
                                created_zip = save_to_zip(file_list, zip_output_name)
                        #if 'profile' in st.session_state and 'submitted' in st.session_state:

                            # Botón de descarga para el archivo zip en Streamlit
                                with open(created_zip, "rb") as f:
                                    st.download_button(
                                        label="Descargar informe y anexos",
                                        data=f,
                                        file_name=zip_output_name,
                                        mime="application/zip",
                                        on_click=reset_app
                                        )

                                    # Opcional: Eliminar los archivos fuente para limpieza
                                for file_name in file_list:
                                    os.remove(file_name)
                            except:
                                print('se ejecutará si el usuario cambia abruptamente de tipo de seleccion de todas las columnas a una sola despuesde haber guardado el formulario')
                                #st.error('Recuerde seleccionar las columnas para el análisis', icon="🚨")
                        
                    

                    


# 10.2 segundo condicional, el objetivos es hacer un analisis mínimo, en este tipo de analisis no se tienen en cuenta cosas como la auto correlación, simplemente es un EDA muy sencillo con diagramas de 
        #barras señalando frecuencias en los dato, datos perdidos y algunas medidas de tendencia central. 
    elif mode=='minimal':# empieza el condicional cuando es igual el boton a minimal se ejecutará el código de abajo, a continuación se describen los parametros de ProfileReport para el caso de descripcion minimal:
        profile=ProfileReport(df1, # se toma el df1, que recordando las lineas anteriores, es el df que guarda cualquier modificación hecha por el usuario en la pantalla posterior a la carga de datos
            minimal=True, #en este caso hay que especificar en el paremetro minimal True, dado que por defecto viene en complete, para que haga un EDA básico.
            title="User uploaded table", #título del reporte
            progress_bar=True #  Indica si se debe mostrar una barra de progreso durante la generación del reporte
            ) 
        
        st_profile_report(profile)#se utiliza para mostrar un reporte de análisis exploratorio de datos (EDA) generado por la librería pandas-profiling en la interfaz de Streamlit
                                  #De eliminarse esta línea o no correrse, simplemente la aplicación no mostrará ningún EDA, ni siquierea la progress_bar

        st.session_state['profile'] = profile
            
        if 'generate_report' in st.session_state:        
                    # PONER AQUI EL FORMULARIO
                    with st.form("my_form"):
                        st.title("Formulario Informe de Inspección y Análisis")

                        # Campos de entrada de texto

                        # 1. Encargado del MJD EncargadoMJD

                        EncargadoMJD = st.text_input("Encargado de diligenciar el formato (MJD): ")
                    

                        # 2. ÁreaEncargadoMJD area encargada
                        AreaEncargadoMJD = st.text_input("Área del encargado de diligenciar el formato (MJD):")

                        # 3. Fecha de recepcion o extracción
                        FechaRecepExtrac = st.date_input("Fecha de recepción o extracción:", 
                                                            min_value=datetime(2000, 1, 1), 
                                                            max_value=datetime(2100, 1, 1))
                        FechaRecepExtrac=str(FechaRecepExtrac)




                        st.markdown("Periodo del reporte: ")
                        default_start, default_end = datetime.now() - timedelta(days=1), datetime.now()
                        refresh_value = timedelta(days=1)
                        date_range_string = date_range_picker(picker_type=PickerType.date,
                                                            start=default_start, end=default_end,
                                                            key='date_range_picker',
                                                            refresh_button={'is_show': True, 'button_name': 'Refresh Last 1 Days',
                                                                            'refresh_value': refresh_value})
                        if date_range_string:
                            start, end = date_range_string
                            st.write(f"Date Range Picker [{start}, {end}]")
                            # Suponiendo que start y end son objetos datetime
                            #start_str = start.strftime("%Y-%m-%d")  # Formato de cadena: YYYY-MM-DD
                            #end_str = end.strftime("%Y-%m-%d")  # Formato de cadena: YYYY-MM-DD
                            start_str = str(start)
                            end_str = str(end)


                            # Usar las cadenas en lugar de los objetos datetime
                            #st.write(f"Desde {start_str} hasta {end_str}")
                            date_range_str_out = f"Desde {start_str} hasta {end_str}"

                        
                        # Periodo de actualización 
                        
                        PeriodoActInfo=st.selectbox("Periodicidad de actualización de la información: ", ["Diaria", "Semanal", "Quincenal","Mensual","Bimensual","Trimestral", "Cuatrimestral","Semestral" ,"Anual","Por demanda"])
                            # NombreArchivo        
                        #NombreArchivo=st.write(f"Nombre del archivo cargado: {file_name}")
                        
                        NombreArchivo='archivo'
                        # Tipo de Fuente
                        TipoFuenteInfo= st.selectbox("Tipo de la fuente de información: ", ["Interna", "Externa"])
                        # EntidadesFuenteInfo
                        EntidadesFuenteInfo = st.text_input("Entidad(es) de la fuente de la información:")
                        # contactoEncargadoInfo
                        contactoEncargadoInfo=st.text_input("Contacto encargado de enviar la información:")
                        # dependencia encargado de enviar la informacion
                        DirecEncargadoInfo = st.text_input("Dependencia encargada de enviar la información:")
                        # FuenteEntradaInfo
                        FuenteEntradaInfo=st.selectbox("Fuente de entrada de información: ", ["Acuerdo Formal", "Acuerdo no Formal","Datos Sistemas de Información Internos"])
                        # DireccPagWeb
                        DireccPagWeb=st.text_input('Dirección de la página web (si aplica):')
                        # MedConsEntreInfo
                        MedConsEntreInfo=st.selectbox('Medio de consulta o entrega de la información:',["Oficios","Correos electronicos","Web Services","Servidor de Archivos SFTP","Carpeta Compartida","Otros","No Aplica"])
                        #Formato fuente de información
                        FonrmatInfo= st.selectbox('Formato de la información:', ["Excel","Word","Pdf","Pptx","Web","Txt","Base de Datos","Archivo Plano-CSV","Formulario Web","Web Api"])
                        # Observaciones consistencia
                        ObsConsis=st.text_input("Observaciones consistencia:")
                        #ObsExactSemant exactitud
                        ObsExactSemant=st.text_input("Observaciones Exactitud semántica:")
                        # 'Observaciones Unicidad',ObsUnicidad
                        ObsUnicidad=st.text_input('Observaciones Unicidad:')
                        # ObsComplet 
                        ObsComplet=st.text_input('Observaciones Completitud:')
                        # ('Observaciones Exactitud Sintáctica',)
                        ObsExactSintact=st.text_input('Observaciones Exactitud Sintáctica:')
                        # 'Observaciones Dimensiones mínimas',
                        ObsDimMin=st.text_input('Observaciones Dimensiones mínimas:')
                        # st.write('Observaciones Actualidad',)
                        obsActualidad=st.text_input('Observaciones Actualidad:')
                        #('Observaciones Confiabilidad',)
                        ObsConfiabilid=st.text_input('Observaciones Confiabilidad:')
                        
                        #Cantidad de registros inconsistentes en el df
                        
                        NumRegInconsistentes = st.number_input("Ingrese la cantidad de registros inconsistentes:",step=1,max_value=total_reg_df)
                        
                        #cantidad de registros que carecen de exactitud semántica
                        NumRegsinExacSem= st.number_input("Ingrese la cantidad de registros que carecen de exactitud semántica:",step=1,max_value=total_reg_df)
                        # Botón para enviar el formulario
                        submitted = st.form_submit_button("Guardar Formulario")
                        

                        
                        if submitted:

                            try:

                                st.session_state['submitted'] = True
                                

                                
                                guardar_datos(EncargadoMJD, AreaEncargadoMJD, FechaRecepExtrac, date_range_str_out, PeriodoActInfo,NombreArchivo,TipoFuenteInfo, EntidadesFuenteInfo,
                                            contactoEncargadoInfo, DirecEncargadoInfo, FuenteEntradaInfo, DireccPagWeb, MedConsEntreInfo, FonrmatInfo,ObsConsis, ObsExactSemant,ObsUnicidad,ObsComplet,
                                            ObsExactSintact, ObsDimMin
                                            ,obsActualidad, ObsConfiabilid,NumRegInconsistentes,NumRegsinExacSem)
                                
                                    # Nombre del archivo PDF a generar
                                nombre_archivo = "informe_test.pdf"

                                info_general = {
                                "Encargado de diligenciar el formato (MJD):":EncargadoMJD,
                                "Área del encargado de diligenciar el formato (MJD):":AreaEncargadoMJD,
                                "Fecha de recepción o de extracción:":FechaRecepExtrac,
                                "Periodo del reporte:":date_range_str_out,
                                "Periodicidad de actualización de la información:":PeriodoActInfo,
                                "Nombre del archivo:":NombreArchivo,
                                "Tipo de la fuente de información:":TipoFuenteInfo,
                                "Entidad(es) de la fuente de la información:":EntidadesFuenteInfo,
                                "Contacto encargado de enviar la información:":contactoEncargadoInfo,
                                "Dependencia encargada de enviar la información:":DirecEncargadoInfo,
                                "Fuente de entrada de la información:":FuenteEntradaInfo,
                                "Dirección de la página web (si aplica):":DireccPagWeb,
                                "Medio de consulta o entrega de la información:":MedConsEntreInfo,
                                'Formato de la información:':FonrmatInfo}
                                
                                

                                            
                                calificacion_global_unicidad_str = str(calificacion_global_unicidad)
                                cal_complet_str = str(cal_complet)
                                calificacion_exactitud_str = str(calificacion_exactitud)
                                calificacion_dim_min_df_str = str(calificacion_dim_min_df)
                                calificacion_total_df_str = str(calificacion_total_df)

                                # #calificación de consistencia
                                
                                calificacion_consistencia=((total_reg_df-NumRegInconsistentes)/total_reg_df)*5
                
                                # # Calificación exactitud semantica
                                
                                calificacion_exactitud_semantica=((total_reg_df-NumRegInconsistentes)/total_reg_df)*5

                                tabla_cuantitativa = {
                                0:["Exactitud semántica", calificacion_exactitud, ObsExactSemant],
                                1:["Unicidad", calificacion_global_unicidad, ObsUnicidad],
                                2:["Completitud", cal_complet, ObsComplet],
                                3:["Exactitud (Exactitud sintáctica)",calificacion_exactitud_semantica , ObsExactSintact],
                                4:["Dimensiones mínimas", calificacion_dim_min_df, ObsDimMin],
                                5:["Consistencia", calificacion_consistencia,ObsConsis]}
                                total_calif_todas_dim=(calificacion_exactitud+calificacion_global_unicidad+cal_complet+calificacion_exactitud_semantica+calificacion_dim_min_df+calificacion_consistencia)/6

                                tabla_cuantitativa_para_df = {
                                0:["Exactitud semántica", calificacion_exactitud, ObsExactSemant],
                                1:["Unicidad", calificacion_global_unicidad, ObsUnicidad],
                                2:["Completitud", cal_complet, ObsComplet],
                                3:["Exactitud (Exactitud sintáctica)",calificacion_exactitud_semantica , ObsExactSintact],
                                4:["Dimensiones mínimas", calificacion_dim_min_df, ObsDimMin],
                                5:["Consistencia", calificacion_consistencia,ObsConsis],
                                6:["Total", total_calif_todas_dim,'']}
                                df_calificaciones = pd.DataFrame.from_dict(tabla_cuantitativa_para_df, orient='index', columns=['Categoría', 'Calificación', 'Observaciones'])
                                df_calificaciones['Gráfica calificación'] = df_calificaciones['Calificación'].apply(generar_grafica_estrellas)
                                #df_calificaciones = df_calificaciones[['Categoría', 'Calificación', 'Gráfica Calificación', 'Observaciones']]


                                tabla_cualitativa = {
                                0:["Actualidad", "Todo es actual"],
                                1:["Confiabilidad","Todo es confiable"]}

                                file_pdf=generar_pdf(nombre_archivo, info_general, tabla_cuantitativa, tabla_cualitativa)

                                st.write(df_calificaciones)
                            except:
                                print('el usuario hizo un cambio abrupto de seleccion de todas las columnas a una o varias columnas en su anaisis posterior al dar el boton de guardar en el formulario, esto solo se muestra en la consola')   

                
                    if 'profile' in st.session_state and 'submitted' in st.session_state:
                            try:

                                file = download_profile(profile, output_file="profile_report.html")
                                file_list = ['informe_test.pdf', 'profile_report.html']
                                zip_output_name = 'informe_calidad_informacion.zip'
                                created_zip = save_to_zip(file_list, zip_output_name)
                        #if 'profile' in st.session_state and 'submitted' in st.session_state:

                            # Botón de descarga para el archivo zip en Streamlit
                                with open(created_zip, "rb") as f:
                                    st.download_button(
                                        label="Descargar informe y anexos",
                                        data=f,
                                        file_name=zip_output_name,
                                        mime="application/zip",
                                        on_click=reset_app
                                        )

                                    # Opcional: Eliminar los archivos fuente para limpieza
                                for file_name in file_list:
                                    os.remove(file_name)
                            except:
                                print('el usuario hizo un cambio abrupto de seleccion de todas las columnas a una o varias columnas en su anaisis posterior al dar el boton de guardar en el formulario, esto solo se muestra en la consola')   

