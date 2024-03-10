import streamlit as st
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator
from conversations.conversation_smart import smart_conversations
from conversations.conversation_dumb import dumb_conversations
from streamlit_extras.stylable_container import stylable_container
from conversations.utils import retrieve_convo_by_id
import pandas as pd
import altair as alt

logo_url = '.static/RAGnarok_240.png'

add_logo(logo_url, 60)

convos = {
    "improved": smart_conversations,
    "raw": dumb_conversations,
}

authenticator = get_authenticator()
authenticator._check_cookie()


def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']

    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            #domain=['A', 'B'],
                            domain=[input_text, ''],
                            # range=['#29b5e8', '#155F7A']),  # 31333F
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)

    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response}'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            range=chart_color),  # 31333F
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text


def display_convo_with_eval(convo_id, bot_type):
    convo = retrieve_convo_by_id(convo_id, convos[bot_type])
    interactions = convo["interactions"]
    for interaction in interactions:
        user_message = st.chat_message("User", avatar="🤖")
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
                    st.metric(metric, round(interaction["evaluation"][metric], 2))
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
        if convo["evaluation"]["quality_score"]>0.5:
            donut_color = 'green'
        else:
            donut_color = 'red'
        donut_chart = make_donut(convo["evaluation"]["quality_score"], "quality_score", donut_color)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.altair_chart(donut_chart)
        with col2:
            st.write(convo["evaluation"]["reasoning"])
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