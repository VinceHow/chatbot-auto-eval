import streamlit as st
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator
from conversations.conversation_smart import all_conversations as smart_convos
from conversations.conversation_dumb import all_conversations as dumb_convos
from streamlit_extras.stylable_container import stylable_container
from conversations.utils import retrieve_convo_by_id

logo_url = ".static/RAGnarok_240.png" 

add_logo(logo_url, 60)

convos = {
    "improved": smart_convos,
    "raw": dumb_convos,
}

authenticator = get_authenticator()
authenticator._check_cookie()


def display_convo_with_eval(convo_id, bot_type):
    convo = retrieve_convo_by_id(int(convo_id), convos[bot_type])
    interactions = convo["interactions"]
    for interaction in interactions:
        user_message = st.chat_message("User", avatar="👤")
        thought_message = st.chat_message("Assistant context", avatar="🧠")
        assisstant_message = st.chat_message("Assistant", avatar="🍭")
        user_message.write(interaction["user_query"])
        assisstant_message.write(interaction["bot_response"])
        texts = [knowledge["metadata"]["text"] for knowledge in interaction["knowledge_used"]]
        thought_message.write(texts)
        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px)
                }
                """,
        ):
            st.markdown("Current turn evaluation")
            cols = st.columns([1, 1, 1, 1])
            col_count = 0
            for metric in interaction["evaluation"]:
                with cols[col_count]:
                    st.metric(metric, interaction["evaluation"][metric])
                col_count += 1
    with stylable_container(
        key="container_with_border",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px)
            }
            """,
        ):
        st.markdown("Overall conversation evaluation")
        for metric in convo["evaluation"]:
            st.metric(metric, convo["evaluation"][metric])
    return None


if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
    if "convo_id" in st.query_params and "bot_type" in st.query_params:
        display_convo_with_eval(st.query_params["convo_id"], st.query_params["bot_type"])
    else:
        st.error('Please select a convo to see the detailed eval')
        if st.button("Go back to dashboard"):
            st.switch_page("pages/1🕹️ Evaluation Dashboard.py")
else:
    st.error('Please login to see the detailed eval')
    if st.button("Go back to login"):
        st.switch_page("👋_Welcome.py")