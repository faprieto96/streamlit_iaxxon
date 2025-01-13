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

from plotly.subplots import make_subplots


#st.set_page_config(layout="wide", page_title="IAXXON Pedrera")

#######################################
# API TIEMPO
#######################################





def download_info (query1):
    db_url = 'mysql+mysqlconnector://admin_sos:ADM_sos*01@185.47.245.164/sosein_automatization'
    engine = create_engine(db_url)

    df = pd.read_sql(query1, engine)

    return df


with open(os.path.join(os.getcwd(), 'config.yaml')) as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])



if st.session_state['authentication_status']:
    # Variables
    city = "Pedrera,ES"
    api = "f8b240ffa80eee036066e32f79b95124"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={api}&units=metric"

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


    #######################################
    # CONFIGURACIÓN DE PÁGINA
    #######################################
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
        options = ['7 días','1 hora', '1 día', '2 días',  '1 mes', '1 año']

        # Desplegable para seleccionar el período de tiempo
        time_period = st.selectbox('Selecciona el período de tiempo:', options, )

    with col3:
        st.subheader("Pedrera, Sevilla")
        st.metric(f"Clima en {city}", f"{temp} °C")  # Mostrar temperatura con unidad






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






    query1 = """SELECT signal_name, valor, `Timestamp`
    FROM sosein_automatization.datos_sensores_azure
    where (STR_TO_DATE(`Timestamp`, '%d-%m-%Y %H:%i:%s')> NOW() - INTERVAL var_time_resolution MINUTE) and signal_name IN ('TCAP_VASO', 'TCAP_ACS', 'TC_VASO', 'TF_VASO', 'TPLACAS_SALIDA', 'TDAC_VASO', 'TDS_ACS', 'TDE_ACS', 'TDAF_ACS', 'TDAC_ACS', 'TINT_VASO', 'TINT_ACS', 'TDAF_VASO')
    order by `Timestamp` DESC;"""
    query1 = query1.replace('var_time_resolution', str(var_time_resolution))




    df = download_info (query1)

    from datetime import datetime, timedelta
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M:%S')

    # Definir el rango de minutos hacia atrás
    minutes_back = var_time_resolution
    current_time = datetime.now()  # Puedes usar otro punto de referencia si no es el tiempo actual
    time_threshold = current_time - timedelta(minutes=minutes_back)

    # Filtrar el DataFrame por el rango de tiempo
    df = df[df['Timestamp'] >= time_threshold]

    # Mostrar resultados
    
    #st.write(df)


    df_calculo_kwh = df.copy()

    df_calculo_kwh['Timestamp'] = pd.to_datetime(df_calculo_kwh['Timestamp'])





    # Floor datetime to the nearest hour
    df_calculo_kwh["Timestamp_hour"] = df_calculo_kwh["Timestamp"].dt.floor("H")

    # Group by variable and hourly Timestamp, and calculate mean
    df_calculo_kwh_result = df_calculo_kwh.groupby(["signal_name", "Timestamp_hour"])["valor"].mean().reset_index()
    pivot_df = df_calculo_kwh_result.pivot_table(index='Timestamp_hour', columns='signal_name', values='valor', aggfunc='first')

    # Resetear el índice para que 'timestamp' sea una columna normal
    pivot_df.reset_index(inplace=True)
    pivot_df['kwh'] = (3*(pivot_df['TINT_ACS'] - pivot_df['TDE_ACS'])*0.046) + (4*(pivot_df['TINT_VASO']-pivot_df['TPLACAS_SALIDA'])*0.046)
    pivot_df['kwh_positive'] = pivot_df['kwh'].apply(lambda x: x if x > 0 else 0)

    generacion_kwh = pivot_df[pivot_df['kwh']>0]['kwh'].sum()
    generacion_pellets = float(generacion_kwh/4.9)

    st.write('')
    st.write('')
    st.write('')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Datos de Producción Energía')
        st.metric(f"Ahorro Producido en {city}", f"{round(generacion_kwh,2)} kWh")

    with col2:
        st.subheader('Producción equivalente de Pellets')
        st.metric(f"Producción en Kgs", f"{round(generacion_pellets,2)} Kgs")

    fig1 = go.Figure()
    fig1 = px.line(
        pivot_df,
        x='Timestamp_hour',
        y='kwh_positive',
        labels={'Timestamp_hour': 'Hora del Día', 'kwh_positive': 'Generación (kWh)'},
        markers=True  # Agregar puntos para las horas específicas
    )

    # Personalizar el diseño (opcional)
    fig1.update_layout(
        xaxis_title="Hora del Día",
        yaxis_title="Generación (kWh)",
        #xaxis=dict(tickformat="%H:%M"),  # Mostrar solo hora y minutos
        template="plotly_white",
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)




    df_query1 = df.copy()

    df_query1.rename(columns={'signal_name': 'Nombre del sensor', 'valor': 'Temperatura detectada', 'Timestamp': 'Última actualización'}, inplace=True)
    # Parte de seguridad, pero la query ya está haciendo el trabajo


    ####### MAKE A PLOT - TEMPERATURAS

    if st.session_state["username"] == 'iaxxon':

        query_all= """SELECT signal_name, valor, `Timestamp`
        FROM sosein_automatization.datos_sensores_azure
        where (STR_TO_DATE(`Timestamp`, '%d-%m-%Y %H:%i:%s')> NOW() - INTERVAL var_time_resolution MINUTE)
        order by `Timestamp` DESC;"""
        query_all = query_all.replace('var_time_resolution', str(var_time_resolution))

        df = download_info (query_all)
        df_test_temp = df.copy()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M:%S')

        # Definir el rango de minutos hacia atrás
        minutes_back = var_time_resolution
        current_time = datetime.now()  # Puedes usar otro punto de referencia si no es el tiempo actual
        time_threshold = current_time - timedelta(minutes=minutes_back)

        # Filtrar el DataFrame por el rango de tiempo
        df = df[df['Timestamp'] >= time_threshold]
        df.rename(columns={'signal_name': 'Nombre del sensor', 'valor': 'Temperatura detectada', 'Timestamp': 'Última actualización'}, inplace=True)
        df_test_temp = df.copy()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TCAP_ACS']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TCAP_ACS']['Temperatura detectada'], name = 'TCAP_ACS'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TF_VASO']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TF_VASO']['Temperatura detectada'], name = 'TF_VASO'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TPLACAS_SALIDA']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TPLACAS_SALIDA']['Temperatura detectada'], name = 'TPLACAS_SALIDA'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TCAP_VASO']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TCAP_VASO']['Temperatura detectada'], name = 'TCAP_VASO'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TC_VASO']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TC_VASO']['Temperatura detectada'], name = 'TC_VASO'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TDAC_VASO']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TDAC_VASO']['Temperatura detectada'], name = 'TDAC_VASO'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TDS_ACS']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TDS_ACS']['Temperatura detectada'], name = 'TDS_ACS'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TDE_ACS']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TDE_ACS']['Temperatura detectada'], name = 'TDE_ACS'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TDAF_ACS']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TDAF_ACS']['Temperatura detectada'], name = 'TDAF_ACS'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TDAC_ACS']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TDAC_ACS']['Temperatura detectada'], name = 'TDAC_ACS'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TINT_VASO']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TINT_VASO']['Temperatura detectada'], name = 'TINT_VASO'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TINT_ACS']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TINT_ACS']['Temperatura detectada'], name = 'TINT_ACS'))
        fig.add_trace(go.Line(x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='TDAF_VASO']['Última actualización']), y=df_test_temp[df_test_temp['Nombre del sensor']=='TDAF_VASO']['Temperatura detectada'], name = 'TDAF_VASO'))
        # Bar traces for binary state data
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='V_ACS']['Última actualización']),
            y=df_test_temp[df_test_temp['Nombre del sensor']=='V_ACS']['Temperatura detectada'],
            name='Ventilador ACS',
        ), secondary_y=True)
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='V_Vaso']['Última actualización']),
            y=df_test_temp[df_test_temp['Nombre del sensor']=='V_Vaso']['Temperatura detectada'],
            name='Ventilador Vaso',
        ), secondary_y=True)
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='B_ACS']['Última actualización']),
            y=df_test_temp[df_test_temp['Nombre del sensor']=='B_ACS']['Temperatura detectada'],
            name='Bomba ACS',
        ), secondary_y=True)
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='B_D_Vaso']['Última actualización']),
            y=df_test_temp[df_test_temp['Nombre del sensor']=='B_D_Vaso']['Temperatura detectada'],
            name='Bomba Deposito Vaso',
        ), secondary_y=True)
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df_test_temp[df_test_temp['Nombre del sensor']=='A_PVaso']['Última actualización']),
            y=df_test_temp[df_test_temp['Nombre del sensor']=='A_PVaso']['Temperatura detectada'],
            name='Accionamiento Intercambiador Placas a Vaso',
        ), secondary_y=True)

        # Layout adjustments
        fig.update_layout(
            xaxis_title="Datos de temperatura",
            yaxis_title="Grados Centígrados (ºC)",
            yaxis2_title="Estado (Binario)",
            template="plotly_white",
            hovermode='x unified',
            barmode='overlay'  # Bars overlay instead of stacking
        )
        st.subheader("Histórico datos de temperatura")
        st.plotly_chart(fig, use_container_width=True)
