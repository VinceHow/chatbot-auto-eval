import streamlit as st
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator
from conversations.conversation_smart import all_conversations as smart_convos
from conversations.conversation_dumb import all_conversations as dumb_convos
from conversations.utils import extract_traditional_metrics_from_convos, extract_job_to_be_done_metrics
from config import heroku_url, local_url, get_running_environment, traditional_metrics

logo_url = ".static/RAGnarok_240.png" 

add_logo(logo_url, 60)

convos = {
    "improved": smart_convos,
    "raw": dumb_convos
}

if "running_environment" not in st.session_state:
    st.session_state.running_environment = get_running_environment()


def display_detail_eval(metric_name, bot_type):
    st.markdown(f"### Detailed Eval for '{metric_name}' for bot version {bot_type}")
    base_url = heroku_url if st.session_state.running_environment == "Heroku" else local_url
    conversations = convos[bot_type]
    if metric_name in traditional_metrics:
        metric_info = extract_traditional_metrics_from_convos(metric_name, conversations, base_url, bot_type)
        avg_value = metric_info["value"].mean()
        st.metric(metric_name, avg_value)
        st.dataframe(metric_info, 
                    column_config={
                        "conversation_id": "Conversation ID",
                        "value": st.column_config.NumberColumn(
                            "Metric value",
                            help="Avg result of the metric for the conversation",
                        ),
                        "convo_link": st.column_config.LinkColumn("Conversation URL", display_text="Open conversation"),
                        "convo_history": "Conversation history"
                        },
                    hide_index=True)
    else:
        metric_info = extract_job_to_be_done_metrics(metric_name, conversations, base_url, bot_type)
        metric_keys = metric_info["metric_list"].iloc[0]
        column_config = {
            "conversation_id": "Conversation ID",
            "convo_link": st.column_config.LinkColumn("Conversation URL", display_text="Open conversation"),
            "convo_history": "Conversation history"
        }
        column_config.update({key: st.column_config.NumberColumn(key, help="Metric value") for key in metric_keys})
        st.dataframe(metric_info, column_config=column_config, hide_index=True)


authenticator = get_authenticator()
authenticator._check_cookie()

if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
    if "metric_name" in st.query_params and "bot_type" in st.query_params:
        display_detail_eval(st.query_params["metric_name"], st.query_params["bot_type"])
    else:
        st.error('Please select a metric to see the detailed eval')
        if st.button("Go back to dashboard"):
            st.switch_page("pages/1🕹️ Evaluation Dashboard.py")
else:
    st.error('Please login to see the detailed eval')
    if st.button("Go back to login"):
        st.switch_page("👋_Welcome.py")
