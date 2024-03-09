import streamlit as st
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator

add_logo("http://placekitten.com/120/120")

def display_detail_eval(metric_name):
    st.markdown(f"### Detailed Eval for {metric_name}")

authenticator = get_authenticator()
authenticator._check_cookie()

if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
    if "metric_name" in st.query_params:
        display_detail_eval(st.query_params["metric_name"])
    else:
        st.error('Please select a metric to see the detailed eval')
        if st.button("Go back to dashboard"):
            st.switch_page("pages/1🕹️ Evaluation Dashboard.py")
else:
    st.error('Please login to see the detailed eval')
    if st.button("Go back to login"):
        st.switch_page("👋_Welcome.py")
