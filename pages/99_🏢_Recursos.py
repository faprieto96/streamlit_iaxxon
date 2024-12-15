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

st.markdown(
    """
    Bienvenido a IAXXON Solar Energy, la 1ª y única empresa española con patente propia de energía Solar Térmica de aire. 

    La tecnología más revolucionaria y rentable para el ahorro en calefacción, deshumectación, agua caliente y calor para procesos industriales.
    """
)