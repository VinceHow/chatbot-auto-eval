import streamlit as st
import pandas as pd
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator
import time
from config import jobs_to_be_done_info, heroku_url, local_url, get_running_environment

logo_url = '.static/RAGnarok_240.png'

add_logo(logo_url, 60)
        
authenticator = get_authenticator()
authenticator._check_cookie()

jobs_to_be_done_metrics = [metric["job-to-be-done"] for metric in jobs_to_be_done_info]

if "jobs_to_be_done" not in st.session_state:
    st.session_state.jobs_to_be_done = jobs_to_be_done_metrics
if "running_environment" not in st.session_state:
    st.session_state.running_environment = get_running_environment()


def submit():
    if st.session_state.text_input not in st.session_state.jobs_to_be_done:
        st.session_state.jobs_to_be_done.append(st.session_state.text_input)
    st.session_state.text_input = ''


def user_input_flow():
    if st.session_state.running_environment == "Heroku":
        base_url = heroku_url
    else:
        base_url = local_url
    user_input = st.text_input('Tell us what you want the chatbot to achieve by talking to the customers', key='text_input', placeholder=jobs_to_be_done_metrics[0], on_change=submit)
    selected_goals = st.multiselect('Select the goals you want to evaluate the chatbot on', st.session_state.jobs_to_be_done)
    st.text_input('Name of the version of the chatbot you want to evaluate', value="raw")
    if st.button('Generate evaluation suite'):
        with st.status("Auto generating evaluation suite...", expanded=True):
            st.write("Reading knowledge base...")
            time.sleep(1)
            st.write("Simulating mutli-turn conversation with desired bot...")
            time.sleep(3)
            st.write("Running evaluation metrics...")
            time.sleep(3)
        url = f"{base_url}/Evaluation_Dashboard"
        st.link_button("Go to the evaluation suite", url)

        

if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
    user_input_flow()
else:
    st.warning('Please login to see the evaluation dashboard')
    if st.button("Go back to login"):
        st.switch_page("👋_Welcome.py")