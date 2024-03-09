import streamlit as st
from streamlit_extras.app_logo import add_logo

add_logo("http://placekitten.com/120/120")


metric_infos = [
    {"name": "Faithfulness", "value": 0.9, "status": "pass"},
    {"name": "Context_precision", "value": 0.8, "status": "pass"},
    {"name": "Answer_relevancy", "value": 0.3, "status": "fail"},
    {"name": "Context_recall", "value": 0.1, "status": "fail"},
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
        url = f"http://localhost:8501/Eval_deepdive?metric_name={metric_info['name']}"
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
        

if "authentication_status" not in st.session_state:
    st.switch_page("👋_Welcome.py")
else:
    if st.session_state["authentication_status"]:
        evaluation_dashboard()
    else:
        st.switch_page("👋_Welcome.py")