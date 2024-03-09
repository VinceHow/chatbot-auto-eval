import streamlit as st
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator
from config import heroku_url, local_url, get_running_environment

logo_url = "../assets/RAGnarok_240.png" 

add_logo(logo_url, 60)

if "running_environment" not in st.session_state:
    st.session_state.running_environment = get_running_environment()

metric_infos = [
    {"name": "faithfulness", "value": 0.9, "status": "pass"},
    {"name": "context_precision", "value": 0.8, "status": "pass"},
    {"name": "answer_relevancy", "value": 0.3, "status": "fail"},
    {"name": "context_recall", "value": 0.1, "status": "fail"},
]


def traditional_meteric_row(metric_info):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if metric_info["status"]=="pass":
            st.markdown("✅")
        elif metric_info["status"]=="fail":
            st.markdown("❌")
    with col2:
        st.metric(metric_info["name"], metric_info["value"])
    with col3:
        if st.session_state.running_environment == "Heroku":
            url = f"{heroku_url}/Eval_deepdive?metric_name={metric_info['name']}"
        else:
            url = f"{local_url}/Eval_deepdive?metric_name={metric_info['name']}"
        st.link_button("Detailed Eval", url)


def evaluation_dashboard():
    st.title('Evaluation Dashboard')
    title_bot_col, bot_version_col = st.columns([3, 1])
    with title_bot_col:
        st.markdown("### Snack 52 customer acquisition bot")
    with bot_version_col:
        st.session_state.bot_version = st.selectbox(
        'Bot Version',
        ('dumb', 'smart'))
    tab1, tab2 = st.tabs(["RAG specific metrics", "Jobs to be done metrics"])
    with tab1:
        st.markdown("### Traditional RAG metrics")
        for metric_info in metric_infos:
            traditional_meteric_row(metric_info)
    with tab2:
        st.markdown("### Jobs to be done metrics")
        
authenticator = get_authenticator()
authenticator._check_cookie()

if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
    evaluation_dashboard()
else:
    st.warning('Please login to see the evaluation dashboard')
    if st.button("Go back to login"):
        st.switch_page("👋_Welcome.py")