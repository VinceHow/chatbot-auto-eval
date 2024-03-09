import streamlit as st

def evaluation_dashboard():
    pass

if st.session_state["authentication_status"]:
    evaluation_dashboard()
else:
    st.switch_page("👋_Welcome.py")