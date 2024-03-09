import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

@st.cache_resource(experimental_allow_widgets=True, show_spinner=False)
def get_authenticator():
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    return authenticator
