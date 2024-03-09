import streamlit as st
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator
from streamlit_extras.stylable_container import stylable_container

logo_url = ".static/RAGnarok_240.png" 

add_logo(logo_url, 60)

authenticator = get_authenticator()
authenticator._check_cookie()

def display_convo_with_eval(convo_id):
    # assuming this is the convo
    convo = {
        "id": "1",
        'conversation_seed': {'job_to_be_done': 'Discover new and unique snacks', 'user_query': 'What kind of snacks can I expect in each box?'}, 
        'interactions': [
            {'interaction_turn': 1, 'user_query': 'What kind of snacks can I expect in each box?', 'bot_response': "Each Snack 52 box contains a curated selection of premium, artisanal snacks from around the world. You'll discover unique flavors, healthy options, and indulgent treats tailored to your preferences. Our snack experts carefully source the finest snacks to delight your taste buds every month.", 'knowledge_used': [], 'evaluation': {'faithfulness': 0.0, 'context_precision': 0.0, 'answer_relevancy': 0.0, 'context_recall': 0.0}},
            {'interaction_turn': 2, 'user_query': 'What kind of snacks can I expect in each box?', 'bot_response': "Each Snack 52 box contains a curated selection of premium, artisanal snacks from around the world. You'll discover unique flavors, healthy options, and indulgent treats tailored to your preferences. Our snack experts carefully source the finest snacks to delight your taste buds every month.", 'knowledge_used': [], 'evaluation': {'faithfulness': 0.0, 'context_precision': 0.0, 'answer_relevancy': 0.0, 'context_recall': 0.0}},
            {'interaction_turn': 3, 'user_query': 'What kind of snacks can I expect in each box?', 'bot_response': "Each Snack 52 box contains a curated selection of premium, artisanal snacks from around the world. You'll discover unique flavors, healthy options, and indulgent treats tailored to your preferences. Our snack experts carefully source the finest snacks to delight your taste buds every month.", 'knowledge_used': [], 'evaluation': {'faithfulness': 0.0, 'context_precision': 0.0, 'answer_relevancy': 0.0, 'context_recall': 0.0}}
            ], 
        'interaction_turns': 3,
        'evaluation': "passed"
    }
    interactions = convo["interactions"]
    for interaction in interactions:
        user_message = st.chat_message("User", avatar="👤")
        assisstant_message = st.chat_message("Assistant", avatar="🍭")
        user_message.write(interaction["user_query"])
        assisstant_message.write(interaction["bot_response"])
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
            st.markdown("This is a container with a border.")
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
        st.markdown("This is a container with a border.")
    return None


if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
    display_convo_with_eval("1")
    # if "convo_id" in st.query_params:
    #     display_convo_with_eval(st.query_params["convo_id"])
    # else:
    #     st.error('Please select a convo to see the detailed eval')
    #     if st.button("Go back to dashboard"):
    #         st.switch_page("pages/1🕹️ Evaluation Dashboard.py")
else:
    st.error('Please login to see the detailed eval')
    if st.button("Go back to login"):
        st.switch_page("👋_Welcome.py")