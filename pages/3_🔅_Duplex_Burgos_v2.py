import streamlit as st
import streamlit_authenticator as stauth

import pandas as pd
import yaml
from yaml.loader import SafeLoader

import plotly.express as px
import plotly.graph_objects as go

import requests

# Database connection parameters
from sqlalchemy import create_engine, text
import os


#####################################################################################################################
# Configuración página
#####################################################################################################################

# Variables
city = "Burgos,ES"
api = "f8b240ffa80eee036066e32f79b95124"
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={api}&units=metric"
Nombre_complejo_instalacion = "Burgos, España"



#####################################################################################################################
# API TIEMPO
#####################################################################################################################


if st.session_state['authentication_status']:
    # Variables


    # Solicitar datos del clima
    response = requests.get(url)
    x = response.json()

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        try:
            # Extraer temperatura y convertir a grados Celsius
            cel = 273.15
            temp = round(x["main"]["temp"], 2)  # Convertir de Kelvin a Celsius

            # Obtener el ícono del clima
            icon = x["weather"][0]["icon"]
            url_png = f'http://openweathermap.org/img/w/{icon}.png'
        except KeyError as e:
            st.error(f"Error en los datos recibidos: {str(e)}")
    else:
        st.error(f"Error al obtener los datos del clima: {x.get('message', 'Respuesta inesperada')}")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Custom HTML/CSS for the banner
        custom_html = """
        <div class="banner">
            <img src="https://i.imgur.com/SJQWq0F.png" alt="Banner Image">
        </div>
        <style>
        .banner {
            margin: 0px;
            margin-bottom: 20px;
            width: 100%;
            min-width: 110px;
            max-width: 140px;
            position: relative;
            height: auto;
            min-height: 40px;
            max-height: 100px;
            overflow: hidden;
        }
        .banner img {
            max-width : 140px;
            max-width : 140px;
            width: 100%;
            position: absolute;
        }
        </style>
        """

        # Display the custom HTML
        st.markdown(custom_html, unsafe_allow_html=True)
        # Lista de opciones para el desplegable
        options = ['7 días', '1 hora', '1 día', '2 días', '1 mes', '1 año']
        time_period = st.selectbox('Selecciona el período de tiempo:', options)

        def calculo_horas(time_period):
            if time_period=='1 hora':
                var_salida = 60
            elif time_period == '1 día':
                var_salida = 60*24
            elif time_period == '2 días':
                var_salida = 60*24*2
            elif time_period == '7 días':
                var_salida = 60*24*7
            elif time_period == '1 mes':
                var_salida = 60*24*30
            elif time_period == '1 año':
                var_salida = 60*24*365
            return var_salida


        var_time_resolution = calculo_horas(time_period)

    with col3:
        st.subheader("Duplex Burgos")
        st.metric(f"Clima en {city}", f"{temp} °C")  # Mostrar temperatura con unidad


#####################################################################################################################
#####################################################################################################################
# CARGA DE DATOS  -- ALBERTO
#######################################

#######################################
# DISEÑO PÁGINA STREAMLIT
#######################################


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
SELECT instalacion, datetime, TCAP, TEXT, TDAC, TINT, TAC1, TRET,TDAF, fan, pump, heat
FROM sosein_automatization.sensor_data_iaxxon AS s
WHERE instalacion = '869951035512445' and (datetime > NOW() - INTERVAL var_time_resolution MINUTE)
order by datetime desc;
"""

query1 = query1.replace('var_time_resolution', str(var_time_resolution))
df_test = download_info (query1)
from datetime import datetime, timedelta
df_test['datetime'] = pd.to_datetime(df_test['datetime'], format='%d-%m-%Y %H:%M:%S')

# Definir el rango de minutos hacia atrás
minutes_back = var_time_resolution
current_time = datetime.now()  # Puedes usar otro punto de referencia si no es el tiempo actual
time_threshold = current_time - timedelta(minutes=minutes_back)

df_test.fillna(0, inplace=True)
df_test['energia_producida'] = (df_test['TINT'] - df_test['TDAF'])*df_test['pump']* 0.046
df_test['energia_producida'] = df_test['energia_producida'].apply(lambda x: x if x > 0 else 0)


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Temperatura Captador", value=f"{df_test['TCAP'].iloc[-1]} °C")
    st.metric(label="Energía Producida", value=f"{round(df_test['energia_producida'].sum(),2)} kWh")

with col2:
    st.metric(label="Temperatura Intercambiador", value=f"{df_test['TINT'].iloc[-1]} °C")
    st.metric(label="Temperatura Depósito", value=f"{df_test['TDAC'].iloc[-1]} °C")


# Create a plotly figure
from plotly.subplots import make_subplots

st.subheader("Evolución Temperaturas")
fig_agua = go.Figure()
fig_agua.add_trace(go.Line(x=pd.to_datetime(df_test['datetime']), y=df_test['TDAF'], name = 'Temp. Agua fria'))
fig_agua.add_trace(go.Line(x=pd.to_datetime(df_test['datetime']), y=df_test['TDAC'], name = 'Temp Depósito Agua Caliente'))
fig_agua.add_trace(go.Line(x=pd.to_datetime(df_test['datetime']), y=df_test['TCAP'], name = 'Temp. Captador'))
fig_agua.add_trace(go.Line(x=pd.to_datetime(df_test['datetime']), y=df_test['TINT'], name = 'Temp Intercambiador'))
fig_agua.update_layout(
    xaxis_title="Temperatura Captador",
    yaxis_title="Grados Centígrados (ºC)",
    #xaxis=dict(tickformat="%H:%M"),  # Mostrar solo hora y minutos
    template="plotly_white",
    hovermode='x unified'
)
st.plotly_chart(fig_agua, use_container_width=True)




if st.session_state["username"] == 'iaxxon':
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df_test_temp = df_test

    fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp['datetime']), y=df_test_temp['TCAP'], name = 'TCAP'))
    fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp['datetime']), y=df_test_temp['TDAC'], name = 'TDAC'))
    fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp['datetime']), y=df_test_temp['TINT'], name = 'TINT'))
    fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp['datetime']), y=df_test_temp['TINT'], name = 'TDAF'))

    # Bar traces for binary state data
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(df_test_temp['datetime']),
        y=df_test_temp['fan'],
        name='Fan (Estado)',
    ), secondary_y=True)
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(df_test_temp['datetime']),
        y=df_test_temp['pump'],
        name='Pump (Estado)',
    ), secondary_y=True)
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(df_test_temp['datetime']), 
        y=df_test_temp['heat'], 
        name='Heat (Estado)', 
    ), secondary_y=True)

    # Layout adjustments
    fig.update_layout(
        xaxis_title="Datos de temperatura",
        yaxis_title="Grados Centígrados (ºC)",
        yaxis2_title="Estado (Binario)",
        yaxis2=dict(range=[0, 1.1]),  # Match binary state values
        template="plotly_white",
        hovermode='x unified',
        barmode='overlay'  # Bars overlay instead of stacking
    )
    st.subheader("Histórico datos de temperatura")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Información recibida")
    st.dataframe(df_test)