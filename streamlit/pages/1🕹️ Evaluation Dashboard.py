import streamlit as st
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator
from conversations.conversation_smart import all_conversations as smart_convos
from conversations.conversation_dumb import all_conversations as dumb_convos
from conversations.utils import extract_traditional_metrics_from_convos, summarise_traditional_metrics, extract_job_to_be_done_metrics, summarise_jtd_metrics
from config import heroku_url, local_url, get_running_environment, traditional_metrics, jobs_to_be_done_info

logo_url = ".static/RAGnarok_240.png" 

add_logo(logo_url, 60)

if "bot_version" not in st.session_state:
    st.session_state.bot_version = "raw"
if "running_environment" not in st.session_state:
    st.session_state.running_environment = get_running_environment()

convos = {
    "improved": smart_convos,
    "raw": dumb_convos
}


def traditional_meteric_row(metric_info, base_url):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if metric_info["status"]=="pass":
            st.markdown("✅")
        elif metric_info["status"]=="fail":
            st.markdown("❌")
    with col2:
        st.metric(metric_info["name"], metric_info["value"])
    with col3:
        url = f"{base_url}/Eval_deepdive?metric_name={metric_info['name']}&bot_type={st.session_state.bot_version}"
        st.link_button("Detailed Eval", url)


def jbt_metric_row(metric_info, base_url):
    col1, col2, col3, col4, col5= st.columns([1, 1, 1, 1, 1])
    with col1:
        st.markdown(metric_info["name"])
        st.markdown(f"Explaination: {metric_info['info']}")
    with col2:
        metric_info_keys = list(metric_info.keys())
        for key in metric_info_keys:
            if key not in ["name", "value", "status", "info", "number_of_convo"]:
                st.metric(key, metric_info[key])
    with col3:
        if metric_info["status"]=="pass":
            st.markdown("✅")
        elif metric_info["status"]=="fail":
            st.markdown("❌")
    with col4:
        st.metric("Conversations no.", metric_info["number_of_convo"])
    with col5:
        url = f"{base_url}/Eval_deepdive?metric_name={metric_info['name']}&bot_type={st.session_state.bot_version}"
        st.link_button("Detailed Eval", url)


def evaluation_dashboard():
    st.title('Evaluation Dashboard')
    if st.session_state.running_environment == "Heroku":
        base_url = heroku_url
    else:
        base_url = local_url
    title_bot_col, bot_version_col = st.columns([3, 1])
    with title_bot_col:
        st.markdown("### Snack 52 customer acquisition bot")
    with bot_version_col:
        st.session_state.bot_version = st.selectbox(
        'Bot Version',
        ('raw', 'improved'))
    conversations = convos[st.session_state.bot_version]
    tab1, tab2 = st.tabs(["Jobs to be done metrics", "RAG specific metrics"])
    with tab1:
        st.markdown("### Jobs to be done metrics")
        st.markdown('')
        metric_infos = []
        jobs_to_be_done_metrics = [metric["job-to-be-done"] for metric in jobs_to_be_done_info]
        jobs_to_be_done_extra_info = [metric["need-and-motivation"] for metric in jobs_to_be_done_info]
        for metric, extra_info in zip(jobs_to_be_done_metrics, jobs_to_be_done_extra_info):
            jbt_metrics_df = extract_job_to_be_done_metrics(metric, conversations, base_url, st.session_state.bot_version)
            metric_extracted = summarise_jtd_metrics(jbt_metrics_df)
            metric_extracted["info"] = extra_info
            metric_infos.append(metric_extracted)
        for metric_info in metric_infos:
            jbt_metric_row(metric_info, base_url)
    with tab2:
        st.markdown("### Traditional RAG metrics")
        st.markdown('')
        metric_infos = []
        for metrics in traditional_metrics:
            traditional_metrics_df = extract_traditional_metrics_from_convos(metrics, conversations, base_url, st.session_state.bot_version)
            metric_infos.append(summarise_traditional_metrics(traditional_metrics_df))
        for metric_info in metric_infos:
            traditional_meteric_row(metric_info, base_url)
        
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