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










if st.session_state['roles'] == "admin":
    pages = {
        "Instalaciones disponibles": [
            st.Page("pages/0_🔅_Pedrera.py", title="Pedrera"),

            st.Page("pages/1_🔅_Arjona_CF.py", title="Arjona"),

            st.Page("pages/2_🔅_Estepa_Pabellón.py", title="Pabellón de Estepa"),
            st.Page("pages/2_🔅_Estepa_Piscina.py", title="Piscina de Estepa"),
            st.Page("pages/2_🔅_Estepa_Campo_Futbol.py", title="Campo de Fútbol de Estepa"),

            st.Page("pages/3_🔅_Duplex_Burgos.py", title="Duplex"),

            st.Page("pages/4_🔅_Colegio_do_Brasil.py", title="Colegio do Brasil"),

            st.Page("pages/5_🔅_Huerto_Vega_Pabellón.py", title="Huerto Vega Pabellón"),

            st.Page("pages/6_🔅_Pabellón_Aguilar.py", title="Pabellón, Aguilar"),

            st.Page("pages/7_🔅_Piscina_Priego.py", title="Piscina de Priego"),

            st.Page("pages/8_🔅_Toyota_Hispaljarafe.py", title="Toyota Hispaljarafe"),

            st.Page("pages/9_🔅_Camping_Arcoiris.py", title="Camping Arcoiris"),

            st.Page("pages/10_🔅_Villanueva_CF.py", title="CF Villanueva de Córdoba"),
            st.Page("pages/10_🔅_Villanueva_Piscina.py", title="Piscina Villanueva de Córdoba"),

            st.Page("pages/11_🔅_CF_Villario.py", title="CF Villario"),

        ],
        "Recursos": [
            st.Page("pages/99_🏢_Recursos.py", title="Conoce IAXXON"),
            st.Page("pages/99_🔧_Soporte.py", title="Soporte Técnico"),
        ],
    }


else:
    pages = {
        "Resources": [
            st.Page("pages/99_🏢_Recursos.py", title="Conoce IAXXON"),
        ],
    }

pg = st.navigation(pages)
pg.run()

