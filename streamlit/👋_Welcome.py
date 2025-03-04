import os
import uuid
from datetime import datetime

# from openai import OpenAI
from openai import OpenAI
from streamlit_extras.app_logo import add_logo
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from authenticator.authenticate import get_authenticator
from config import get_running_environment

if "running_environment" not in st.session_state:
    st.session_state.running_environment = get_running_environment()

logo_url = '.static/RAGnarok_240.png' 

add_logo(logo_url, 60)

st.title('Welcome to RAGnarok - the chatbot auto evaluation tool 🤖🔍🚀')

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = get_authenticator()

authenticator.login()

if st.session_state["authentication_status"]:
    st.markdown('You are logged in. Feel free to navigate to the evaluation dashboard to see your bot performance')
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
