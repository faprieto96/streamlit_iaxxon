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

st.write('IAXXON Es una emprsea...')