import streamlit as st
import streamlit_authenticator as stauth
from streamlit import session_state as ss

import pandas as pd
import yaml
from yaml.loader import SafeLoader

import plotly.express as px
import plotly.graph_objects as go

import requests

# Database connection parameters
from sqlalchemy import create_engine, text
import os
st.set_page_config(layout="wide", page_title="IAXXON", page_icon="🌟")



# Cargar configuración desde config.yaml
CONFIG_FILENAME = 'config.yaml'
with open(CONFIG_FILENAME) as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)



try:
    authenticator.login()
except Exception as e:
    st.error(e)

with st.sidebar:
    if st.session_state['authentication_status']:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')

if st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')

elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')
    st.info('¿Estás experimentando algún problema? Contacto a francisco@iaxxon.es')




#"Supervisión Instalaciones": [
#            st.Page("pages/00_🔅_Inicio.py", title="Supervisión"),
#        ],
################################################################################################
# Role administrador
if st.session_state['roles'] == "admin":
    pages = {
        "IAXXON": [
            st.Page("pages/00_🔅_Inicio.py", title="Gestión instalaciones"),
        ],
        "Sevilla": [
            st.Page("pages/0_🔅_Pedrera.py", title="Pedrera"),
            st.Page("pages/2_🔅_Estepa_Pabellon_v2.py", title="Pabellón de Estepa"),
            st.Page("pages/2_🔅_Estepa_Piscina_v2.py", title="Piscina de Estepa"),
            st.Page("pages/2_🔅_Estepa_CF_v2.py", title="Campo de Fútbol de Estepa"),
            st.Page("pages/8_🔅_Toyota_Hispaljarafe_v2.py", title="Toyota Hispaljarafe"),
        ],
        "Córdoba": [
            st.Page("pages/6_🔅_Pabellón_Aguilar_v2.py", title="Pabellón, Aguilar"),
            st.Page("pages/7_🔅_Piscina_Priego_v2.py", title="Piscina de Priego"),
            st.Page("pages/10_🔅_Villanueva_CF_v2.py", title="CF Villanueva de Córdoba"),
            st.Page("pages/10_🔅_Villanueva_Piscina_v2.py", title="Piscina Villanueva de Córdoba"),
            st.Page("pages/11_🔅_CF_Villario_v2.py", title="CF Villario"),
        ],
        "Granada": [
            st.Page("pages/5_🔅_Huerto_Vega_Pabellon_v2.py", title="Huerto Vega Pabellón"),
        ],
        "Jaén": [
            st.Page("pages/1_🔅_Arjona_CF_v2.py", title="Arjona CF"),
        ],
        "Madrid": [
            st.Page("pages/4_🔅_Colegio_do_Brasil_v2.py", title="Colegio do Brasil"),
            st.Page("pages/9_🔅_Camping_Arcoiris_v2.py", title="Camping Arcoiris"),
        ],
        "Burgos": [
            st.Page("pages/3_🔅_Duplex_Burgos_v2.py", title="Duplex Burgos"),
        ],
        "Recursos": [
            st.Page("pages/99_🏢_Recursos.py", title="Conoce IAXXON"),
            st.Page("pages/99_🔧_Soporte.py", title="Soporte Técnico"),
        ],
    }

################################################################################################
# Role sin iniciar sesión

else:
    pages = {
        "Resources": [
            st.Page("pages/sin_iniciar_sesion.py", title=""),
        ],
    }

pg = st.navigation(pages)
pg.run()

