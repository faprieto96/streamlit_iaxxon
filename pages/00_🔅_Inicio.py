import streamlit as st
import streamlit_authenticator as stauth
import streamlit_toggle as tog

import pandas as pd
import yaml
from yaml.loader import SafeLoader

import plotly.express as px
import plotly.graph_objects as go

import requests

# Database connection parameters
from sqlalchemy import create_engine, text
import os

from datetime import datetime, timedelta
#####################################################################################################################
# Configuración página
#####################################################################################################################
def download_info (query1):
    db_url = 'mysql+mysqlconnector://admin_sos:ADM_sos*01@185.47.245.164/sosein_automatization'
    engine = create_engine(db_url)
    df = pd.read_sql(query1, engine)

    return df

query1 = """
SELECT instalacion, datetime, TCAP, TEXT, TDAC, TINT, TAC1, TRET, fan, pump, heat
FROM sosein_automatization.sensor_data_iaxxon AS s
WHERE datetime = (
    SELECT MAX(datetime)
    FROM sosein_automatization.sensor_data_iaxxon
    WHERE instalacion = s.instalacion
) order by datetime desc;
"""


df = download_info (query1)

df.drop_duplicates('instalacion', inplace=True)
from datetime import datetime, timedelta
df['datetime'] = pd.to_datetime(df['datetime'], format='%d-%m-%Y %H:%M:%S')
df['Última medida'] = datetime.now()-df['datetime']
df.fillna(0, inplace=True)
df['suma'] = df['TCAP']+ df['TEXT']+df['TDAC']+df['TINT']+df['TAC1']+df['TRET']
df['alerta'] = df['suma'].apply(lambda x: 'si' if x == 0 else 'no')
del df['suma']
mapeo_instalaciones = {
    'piscina_estepa': 'Piscina de Estepa',
    '869951035643216': 'Pabellón de Estepa',
    '869951035512445': 'Dúplex',
    '869951035648587': 'Bodegas Habla',
    '869951035865579': 'Piscina Priego de Córdoba',
    '869951035893563': 'Pabellón de Aguilar de la Fra.',
    '869951035898125': 'CF Estepa',
    'pabellonhuetor': 'Pabellón Huétor Vega',
    '869951036734600': 'Camping Arco Iris',
    '869951036721243': 'Toyota Hispaljarafe',
    'cfarjona': 'CF Arjona',
    'acsdobrasil': 'Colegio Mayor do Brasil',
    'cfvirrio': 'CF Villa del Río',
    'cfvillanueva': 'CF Villanueva de Córdoba',
    'piscina_villanueva': 'Piscina Villanueva de Córdoba',
    'sosein_prueba': 'sosein_prueba'
}

# Agregar una nueva columna al DataFrame con el mapeo
df['Nombre instalacion'] = df['instalacion'].map(mapeo_instalaciones)

df = df[['Nombre instalacion', 'instalacion','Última medida', 'alerta','TCAP', 'TEXT', 'TDAC', 'TINT', 'TAC1', 'TRET', 'fan', 'pump', 'heat', 'datetime']]




df_instalaciones_operando_raro = df[df['alerta']=='si']
listado_instalaciones_raras = df_instalaciones_operando_raro['instalacion']


filtro = df['Última medida'] > timedelta(minutes=15)
df_filtrado = df[filtro]
listado_instalaciones_retraso_datos = df_filtrado['instalacion']


filtro = df['Última medida'] > timedelta(minutes=15)
instalaciones_no_deseadas = list(listado_instalaciones_retraso_datos)+list(listado_instalaciones_raras)
df_filtrado_correctas = df[~df['instalacion'].isin(instalaciones_no_deseadas)]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric('Numero instalaciones ', len(df))

with col2:
    st.metric('Instalaciones correctas', len(df_filtrado_correctas), str(round(len(df_filtrado_correctas)/len(df)*100,1))+'%')
with col3:
    st.metric('Instalaciones con operación extraña', len(df_instalaciones_operando_raro), str(round(-len(df_instalaciones_operando_raro)/len(df)*100,1))+'%')
with col4:
    st.metric('Instalaciones con retraso de datos', len(df_filtrado), str(round(-len(df_filtrado)/len(df)*100,1))+'%')

st.subheader('Instalaciones con avisos por operación extraña')
st.dataframe(df_instalaciones_operando_raro)

st.subheader('Instalaciones con retraso en recibo de datos')
st.dataframe(df_filtrado)

st.subheader('Instalaciones funcionando correctamente')
st.dataframe(df_filtrado_correctas)
