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

if "bot_version" not in st.session_state:
    st.session_state.bot_version = "dumb"
if "running_environment" not in st.session_state:
    st.session_state.running_environment = get_running_environment()

add_logo("http://placekitten.com/120/120")
st.title('Welcome to the chatbot auto eval tool 🤖🔍🚀')

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = get_authenticator()

authenticator.login()

if st.session_state["authentication_status"]:
    st.markdown('You are logged in and now naviagte to eval dashboard to see your bot performance')
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
