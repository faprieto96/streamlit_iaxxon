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
#st.set_page_config(layout="wide")






# Variables
city = "Estepa,ES"
api = "f8b240ffa80eee036066e32f79b95124"
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={api}&units=metric"
Nombre_complejo_instalacion = "Pabellón Estepa"




#####################################################################################################################
# Configuración acceso y autenticación
#####################################################################################################################
with open(os.path.join(os.getcwd(), 'config.yaml')) as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])





#####################################################################################################################
# Configuración base de datos
#####################################################################################################################
import influxdb_client

token = "mqo_DwUps71AVWT_o5seGC3Y4qSskDO0iUiUjLtgIGj_Up4v1kmADazokM9mRUoNv6I6ryDgv7pgQguGcjB3wQ=="
org = "a.marana@equsdesign.com"
host = "https://eastus-1.azure.cloud2.influxdata.com"
bucket = "cf_arjona"

client = influxdb_client.InfluxDBClient(
    url=host,
    token=token,
    org=org, verify_ssl=False
    )







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
        options = ['1 hora', '1 día', '2 días', '7 días', '1 mes', '1 año']
        time_period = st.selectbox('Selecciona el período de tiempo:', options)

    with col3:
        st.subheader(Nombre_complejo_instalacion)
        st.metric(f"Clima en {city}", f"{temp} °C")  # Mostrar temperatura con unidad


#####################################################################################################################
#####################################################################################################################
# CARGA DE DATOS  -- ALBERTO
#######################################

from datetime import datetime, timedelta
def get_data(time_period):

    # Obtener la fecha actual
    end_time = datetime.utcnow()

    if time_period == '1 hora':
        start_time = '1h'
    if time_period == '1 día':
        start_time = '1d'
    elif time_period == '2 días':
        start_time = '2d'
    elif time_period == '7 días':
        start_time = '7d'
    elif time_period == '1 mes':
        start_time = '30d'
    elif time_period == '1 año':
        start_time = '365d'

    # Formatear las fechas en el formato aceptado por InfluxDB


    # Construir la consulta
    query_api = client.query_api()
    query= f'from (bucket: "cf_arjona")\
    |> range(start: -{start_time})\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    result = query_api.query_data_frame(org="a.marana@equsdesign.com", query=query.strip())
    return result

def get_kwh(time_period):

    # Obtener la fecha actual
    end_time = datetime.utcnow()

    if time_period == '1 hora':
        start_time = '1h'
    if time_period == '1 día':
        start_time = '1d'
    elif time_period == '2 días':
        start_time = '2d'
    elif time_period == '7 días':
        start_time = '7d'
    elif time_period == '1 mes':
        start_time = '31d'
    elif time_period == '1 año':
        start_time = '1y'

    # Formatear las fechas en el formato aceptado por InfluxDB

    # Construir la consulta
    query_api = client.query_api()
    query= f'from (bucket: "Estepa_Piscina_v7")\
    |> range(start: -{start_time})\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    result = query_api.query_data_frame(org="a.marana@equsdesign.com", query=query.strip())
    return result

def get_kwh(time_period):

    # Obtener la fecha actual
    end_time = datetime.utcnow()

    if time_period == '1 hora':
        start_time = '1h'
    if time_period == '1 día':
        start_time = '1d'
    elif time_period == '2 días':
        start_time = '2d'
    elif time_period == '7 días':
        start_time = '7d'
    elif time_period == '1 mes':
        start_time = '31d'
    elif time_period == '1 año':
        start_time = '1y'

    # Formatear las fechas en el formato aceptado por InfluxDB
    
    # Construir la consulta   
    query_api = client.query_api()
    query = f'''from(bucket: "Estepa_Piscina_v7")\
    |> range(start: -{start_time})\
    |> filter(fn: (r) => r["_measurement"] == "prueba")\
    |> filter(fn: (r) => r["_field"] == "TINT" or r["_field"] == "pump" or r["_field"] == "TDAF")\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
    |> map(fn: (r) => ({{_start: r._start,_stop: r._stop,result: r.result,_time: r._time,_measurement: r._measurement,_field: "energia_kwh",_value: (float(v: r.TINT) - float(v: r.TDAF)) * float(v: r.pump) * 0.046}}),)\
    |> filter(fn: (r) => r["_field"] == "energia_kwh")\
    |> sum()'''

    result = query_api.query_data_frame(org="a.marana@equsdesign.com", query=query)
    return result

query_api = client.query_api()
query_fan = f'''from(bucket: "Estepa_Piscina_v7")\
    |> range(start: -15m)\
    |> filter(fn: (r) => r["_field"] == "fan")\
    |> aggregateWindow(every: 1m, fn: last, createEmpty: false)\
    |> yield(name: "last")\
'''

query_pump = f'''from(bucket: "Estepa_Piscina_v7")\
    |> range(start: -15m)\
    |> filter(fn: (r) => r._measurement == "prueba")\
    |> filter(fn: (r) => r._field == "pump")
    |> yield(name: "last")\
'''
to_drop = ['result', 'table', '_measurement']
   
dffan = query_api.query_data_frame(org="a.marana@equsdesign.com", query=query_fan)
if not isinstance(dffan, list):
    dffan = [dffan]
dffan = pd.concat(dffan, ignore_index=True)

dffan.drop(to_drop, inplace=True, axis=1)

df = get_data(time_period)
if not isinstance(df, list):
    df = [df]

df = pd.concat(df, ignore_index=True)
df.drop(to_drop, inplace=True, axis=1)
df.sort_values(by='_time', ascending=True, inplace=True)

estado_ventilador = dffan['_value'].iloc[-1]  # Tomamos el último valor de la serie de tiempo
dfpump = query_api.query_data_frame(org="a.marana@equsdesign.com", query=query_pump)
if not isinstance(dfpump, list):
    dfpump = [dfpump]
dfpump = pd.concat(dfpump, ignore_index=True)
dfpump.drop(to_drop, inplace=True, axis=1)

estado_bomba = dfpump['_value'].iloc[-1]  # Tomamos el último valor de la serie de tiempo


df2 = get_kwh(time_period)

df['TCAP']=df['TCAP'].round(2)
df['TDAC']=df['TDAC'].round(2)
df['TINT']=df['TINT'].round(2)
df2['_value']=df2['_value'].round(2)
df.rename(columns = {'_time':'Tiempo'}, inplace = True)

#######################################
# DISEÑO PÁGINA STREAMLIT
#######################################



col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Temperatura Captador", value=f"{df.TCAP.iloc[-1]} °C")
    st.metric(label="Energía Producida", value=f"{df2._value.iloc[-1]} kWh")

with col2:
    st.metric(label="Temperatura Intercambiador", value=f"{df.TINT.iloc[-1]} °C")
    st.metric(label="Temperatura Depósito", value=f"{df.TDAC.iloc[-1]} °C")


st.subheader("Gráficas")
config = {'displayModeBar': False}
st.markdown(
    """
    <style>
    .css-17y5rwz {
        overflow-x: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('''
    <style>
    button[title="View fullscreen"] {
    background-color: #004170cc;
    right: 0;
    color: white;
    }

    button[title="View fullscreen"]:hover {
        background-color:  #004170;
        color: white;
        }
    </styles>
    ''', 
    unsafe_allow_html=True
) 

with st.container():
    fig = px.line(df, x="Tiempo", y="TCAP",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Captador')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit", config=config)

with st.container():
    fig = px.line(df, x="Tiempo", y="TDAC",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Depósito Caliente')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit", config=config)

with st.container():
    fig = px.line(df, x="Tiempo", y="TINT",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Intercambiador')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit", config=config)

with st.container():
    fig = px.line(df, x="Tiempo", y="TDAF",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Depósito Agua Fría')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit", config=config)